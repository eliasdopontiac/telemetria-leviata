/*
 * Telemetria Leviatã 2026 - Firmware SIM7000G + Victron BMV (SmartShunt)
 * Local: Telemetria_2026\Firmware lilygo esp32 sim7000g
 *
 */

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_RX_BUFFER 1024

#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <VeDirectFrameHandler.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <esp_task_wdt.h>
#include <Wire.h>

// --- PINOS LILYGO T-SIM7000G ---
#define UART_BAUD   115200
#define PIN_DTR     25
#define PIN_TX      27
#define PIN_RX      26
#define PWR_PIN     4
#define LED_PIN     12
#define BAT_ADC     35

// --- PINOS OLED ---
#define OLED_SDA    21
#define OLED_SCK    22
#define OLED_ADDR   0x3C
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32

// --- PINO BMV (SmartShunt) ---
#define RX_BMV      34

// --- CREDENCIAIS ---
const char apn[]      = "claro.com.br";
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";
const char* broker    = "test.mosquitto.org";
const int mqtt_port   = 1883;
const char* topic     = "leviata/telemetria/bmv";

// --- OBJETOS ---
#define SerialAT Serial1
TinyGsm        modem(SerialAT);
TinyGsmClient  client(modem);
PubSubClient   mqtt(client);
VeDirectFrameHandler bmv;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// --- VARIÁVEIS DE TEMPO ---
unsigned long lastPublish = 0;
unsigned long lastGPSUpdate = 0;
unsigned long lastDisplayUpdate = 0;
const long intervalPublish = 5000;
const long intervalGPS = 15000;
const long intervalDisplay = 1000;

// --- VARIÁVEIS DE ESTADO ---
float lat = 0, lon = 0, speed = 0;
int signalQuality = 0;
float v_sistema = 0;
uint32_t lastReconnectAttempt = 0;

// --- WATCHDOG CONFIG ---
#define WDT_TIMEOUT 15

float readSystemVoltage() {
    uint32_t raw = 0;
    for(int i=0; i<10; i++) raw += analogRead(BAT_ADC);
    raw /= 10;
    float voltagem = (raw / 4095.0) * 2.0 * 3.3 * 1.1;
    return voltagem;
}

void updateOLED() {
    display.clearDisplay();
    display.setCursor(0, 0);
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);

    display.print("GSM:"); display.print(signalQuality);
    display.print(" Q:"); display.println(mqtt.connected() ? "OK" : "ERR");

    float voltagemBarco = 0;
    for (int i = 0; i < bmv.veEnd; i++) {
        if (String(bmv.veName[i]) == "V") voltagemBarco = atof(bmv.veValue[i]) / 1000.0;
    }

    display.print("V_Barco: "); display.print(voltagemBarco, 1); display.println("V");
    display.print("V_Sist : "); display.print(v_sistema, 2); display.println("V"); // "Sist" para Sistema
    display.print("S:"); display.print(speed, 1); display.print("kmh ");
    display.print("RSSI:"); display.print(signalQuality);

    display.display();
}

void setupModem() {
    Serial.println("--- INICIANDO MODEM SIM7000G ---");
    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    delay(1000);
    digitalWrite(PWR_PIN, LOW);

    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);
    delay(3000);

    if (!modem.restart()) Serial.println("[ERRO] Falha modem");

    modem.setNetworkMode(48);
    modem.waitForNetwork();
    modem.gprsConnect(apn, gprsUser, gprsPass);
    mqtt.setServer(broker, mqtt_port);
    modem.enableGPS();
}

boolean mqttConnect() {
    if (mqtt.connect("Leviata_ESP32_SIM7000G")) {
        return true;
    }
    return false;
}

void collectDataAndPublish() {
    v_sistema = readSystemVoltage();

    StaticJsonDocument<512> doc;
    JsonObject gps = doc.createNestedObject("gps");
    gps["lat"] = lat;
    gps["lon"] = lon;
    gps["speed"] = speed;

    doc["rssi"] = signalQuality;
    doc["v_sistema"] = serialized(String(v_sistema, 2));

    JsonObject dadosBmv = doc.createNestedObject("bmv");
    for (int i = 0; i < bmv.veEnd; i++) {
        String label = String(bmv.veName[i]);
        String value = String(bmv.veValue[i]);
        if (label == "V") dadosBmv["v_mv"] = value.toInt();
        else if (label == "I") dadosBmv["i_ma"] = value.toInt();
        else if (label == "P") dadosBmv["p_w"] = value.toInt();
        else if (label == "SOC") dadosBmv["soc"] = value.toInt();
    }

    char buffer[512];
    serializeJson(doc, buffer);

    if (mqtt.connected()) {
        mqtt.publish(topic, buffer);
        Serial.println("[OK] Enviado: " + String(buffer));
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
}

void setup() {
    Serial.begin(115200);
    Serial2.begin(19200, SERIAL_8N1, RX_BMV, -1);
    pinMode(LED_PIN, OUTPUT);
    pinMode(BAT_ADC, INPUT);

    Wire.begin(OLED_SDA, OLED_SCK);
    if (display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
        display.clearDisplay();
        display.display();
    }

    setupModem();

    esp_task_wdt_init(WDT_TIMEOUT, true);
    esp_task_wdt_add(NULL);
}

void loop() {
    esp_task_wdt_reset();
    while (Serial2.available()) bmv.rxData(Serial2.read());

    if (!mqtt.connected()) {
        uint32_t now = millis();
        if (now - lastReconnectAttempt > 10000) {
            lastReconnectAttempt = now;
            if (mqttConnect()) lastReconnectAttempt = 0;
        }
    } else {
        mqtt.loop();
    }

    if (millis() - lastGPSUpdate > intervalGPS) {
        lastGPSUpdate = millis();
        modem.getGPS(&lat, &lon, &speed);
        signalQuality = modem.getSignalQuality();
    }

    if (millis() - lastPublish > intervalPublish) {
        lastPublish = millis();
        collectDataAndPublish();
    }

    if (millis() - lastDisplayUpdate > intervalDisplay) {
        lastDisplayUpdate = millis();
        updateOLED();
    }
}
