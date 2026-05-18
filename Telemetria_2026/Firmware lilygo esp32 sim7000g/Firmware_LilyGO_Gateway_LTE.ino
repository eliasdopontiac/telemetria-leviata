/*
 * Telemetria Leviatã 2026 - Gateway LTE (LilyGO T-SIM7000G)
 * MODO COMPETIÇÃO - Dual GPS (NEO-6M via ESP-NOW + SIM7000G Interno)
 */

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false

#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <esp_now.h>
#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define UART_BAUD   115200
#define PIN_DTR     25
#define PIN_TX      27
#define PIN_RX      26
#define PWR_PIN     4
#define LED_PIN     12
#define BAT_ADC     35

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_SDA 21
#define OLED_SCK 22
#define OLED_ADDR 0x3C

const char apn[]      = "claro.com.br";
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";
const char* broker    = "test.mosquitto.org";
const int mqtt_port   = 1883;
const char* topic     = "leviata/telemetria/race";

typedef struct __attribute__((packed)) struct_telemetry {
    uint8_t sync_byte; 
    int16_t motor_rpm;
    float motor_corrente_a;
    float motor_v;
    int8_t motor_temp_c;
    int8_t ctrl_temp_c;
    uint8_t far_falha;
    float solar_p_w;
    float solar_i_a;
    float solar_v_v;
    double lat;
    double lng;
    float vel_kmh;
    uint8_t sats;
    uint8_t gps_h;
    uint8_t gps_m;
    uint8_t gps_s;
    float gps_course;
    float gps_hdop;
} struct_telemetry;

struct_telemetry incomingData;
bool newData = false;
float v_sistema = 0;
int signalQuality = 0;

// Variáveis do GPS Interno da LilyGO
float lat_int = 0;
float lon_int = 0;
float speed_int = 0;

#define SerialAT Serial1
TinyGsm        modem(SerialAT);
TinyGsmClient  client(modem);
PubSubClient   mqtt(client);
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

uint32_t lastReconnectAttempt = 0;

void OnDataRecv(const uint8_t * mac, const uint8_t *incoming, int len) {
    if (len == sizeof(incomingData)) {
        memcpy(&incomingData, incoming, sizeof(incomingData));
        if (incomingData.sync_byte == 0xAA) newData = true;
    }
}

float readSystemVoltage() {
    uint32_t raw = 0;
    for(int i=0; i<10; i++) raw += analogRead(BAT_ADC);
    return (raw / 10.0 / 4095.0) * 2.0 * 3.3 * 1.1;
}

void setupModem() {
    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH); delay(1000); digitalWrite(PWR_PIN, LOW);
    delay(1000);
    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);
    modem.restart();
    modem.setNetworkMode(48);
    modem.waitForNetwork(180000L, true);
    modem.gprsConnect(apn, gprsUser, gprsPass);
    mqtt.setServer(broker, mqtt_port);
    
    // Liga o GPS interno do SIM7000G
    modem.enableGPS();
}

boolean mqttConnect() { return mqtt.connect("Leviata_Gateway_LTE"); }

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT); digitalWrite(LED_PIN, HIGH); 
    Wire.begin(OLED_SDA, OLED_SCK); display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
    display.clearDisplay(); display.setTextColor(SSD1306_WHITE);
    display.println("Leviata GATEWAY RACE"); display.display();

    WiFi.mode(WIFI_STA);
    esp_now_init();
    esp_now_register_recv_cb(OnDataRecv);
    setupModem();
}

void loop() {
    if (!modem.isNetworkConnected()) {
        if (modem.waitForNetwork(180000L, true)) modem.gprsConnect(apn, gprsUser, gprsPass);
    }
    if (!mqtt.connected()) {
        if (millis() - lastReconnectAttempt > 10000L) {
            lastReconnectAttempt = millis();
            if (mqttConnect()) lastReconnectAttempt = 0;
        }
        return;
    }
    mqtt.loop();

    if (newData) {
        newData = false;
        v_sistema = readSystemVoltage();
        signalQuality = modem.getSignalQuality();
        
        // Coleta o GPS interno como contingência
        modem.getGPS(&lat_int, &lon_int, &speed_int);

        char timeBuf[9];
        sprintf(timeBuf, "%02d:%02d:%02d", incomingData.gps_h, incomingData.gps_m, incomingData.gps_s);

        StaticJsonDocument<1536> doc;
        
        JsonObject solar = doc.createNestedObject("solar");
        solar["tensao"] = incomingData.solar_v_v;
        solar["corrente"] = incomingData.solar_i_a;
        solar["pot"] = incomingData.solar_p_w;
        
        JsonObject bateria = doc.createNestedObject("bateria");
        bateria["soc"] = 0; 
        bateria["tensao_bat"] = incomingData.motor_v;
        bateria["corrente_liq"] = incomingData.motor_corrente_a;

        JsonObject prop = doc.createNestedObject("prop");
        prop["rpm"] = incomingData.motor_rpm;
        prop["i_motor"] = incomingData.motor_corrente_a;
        prop["t_motor"] = incomingData.motor_temp_c;
        prop["t_ctrl"] = incomingData.ctrl_temp_c;
        prop["fardriver_falha"] = incomingData.far_falha;

        // GPS Principal (NEO-6M vindo da Heltec)
        JsonObject nav = doc.createNestedObject("nav");
        nav["vel"] = incomingData.vel_kmh;
        nav["lat"] = incomingData.lat;
        nav["lon"] = incomingData.lng;
        nav["gps_satelites"] = incomingData.sats;
        nav["gps_hora"] = timeBuf;
        nav["proa"] = incomingData.gps_course;
        nav["hdop"] = incomingData.gps_hdop;
        
        // GPS Backup (SIM7000G Interno)
        JsonObject nav_int = doc.createNestedObject("nav_int");
        nav_int["vel"] = speed_int;
        nav_int["lat"] = lat_int;
        nav_int["lon"] = lon_int;

        JsonObject sinal = doc.createNestedObject("sinal");
        sinal["lora_pacotes"] = 0;
        sinal["lora"] = 0; 
        sinal["lte"] = signalQuality; 

        doc["v_sist"] = serialized(String(v_sistema, 2));

        char buffer[1536];
        serializeJson(doc, buffer);
        
        if (mqtt.publish(topic, buffer)) {
            digitalWrite(LED_PIN, LOW); delay(20); digitalWrite(LED_PIN, HIGH);
        }

        display.clearDisplay(); display.setCursor(0,0);
        display.printf("LTE:%s R:%d V:%0.2f\n", mqtt.connected() ? "OK" : "ERR", signalQuality, v_sistema);
        display.printf("RPM:%d Sol:%0.0fW\n", incomingData.motor_rpm, incomingData.solar_p_w);
        display.display();
    }
}
