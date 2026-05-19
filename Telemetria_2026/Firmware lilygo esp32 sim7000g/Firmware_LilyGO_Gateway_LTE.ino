/*
 * Telemetria Leviatã 2026 - Gateway LTE (LilyGO T-SIM7000G)
 * FIX: Troca do Broker MQTT para HiveMQ (Estável)
 */

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_USE_GPRS true

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
#define OLED_SDA    21
#define OLED_SCK    22
#define OLED_ADDR   0x3C

// --- MUDANÇA AQUI: NOVO BROKER CONFIÁVEL ---
const char apn[]      = "claro.com.br";
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";
const char* broker    = "broker.hivemq.com";
const int   mqttPort  = 1883;
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

struct_telemetry rxData;
volatile bool hasNewData = false;

#define SerialAT Serial1
TinyGsm modem(SerialAT);
TinyGsmClient client(modem);
PubSubClient mqtt(client);
Adafruit_SSD1306 display(128, 32, &Wire, -1);

enum ModemState { MODEM_INIT, WAIT_NETWORK, CONNECT_GPRS, CONNECT_MQTT, MODEM_READY, MODEM_ERROR };
ModemState currentState = MODEM_INIT;
unsigned long lastStateChange = 0;
int retryCount = 0;

float lat_int = 0.0, lon_int = 0.0, speed_int = 0.0;
float v_sistema = 0.0;
int signalQuality = 0;

void IRAM_ATTR OnDataRecv(const esp_now_recv_info *recv_info, const uint8_t *incoming, int len) {
    if (len == sizeof(rxData)) {
        if (incoming[0] == 0xAA) {
            memcpy(&rxData, incoming, sizeof(rxData));
            hasNewData = true;
        }
    }
}

float readSystemVoltage() {
    uint32_t raw = 0;
    for(int i=0; i<10; i++) raw += analogRead(BAT_ADC);
    return (raw / 10.0 / 4095.0) * 2.0 * 3.3 * 1.1;
}

void updateDisplay(const char* statusStr) {
    display.clearDisplay();
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.printf("LTE: %s | CSQ: %d\n", statusStr, signalQuality);
    display.printf("SYS: %0.1fV | RPM: %d\n", v_sistema, rxData.motor_rpm);
    display.printf("BAT: %0.1fV | %0.1fA", rxData.motor_v, rxData.motor_corrente_a);
    display.display();
}

void resetModemHardware() {
    Serial.println("[HW] Ciclo de Power no Modem SIM7000G...");
    digitalWrite(PWR_PIN, HIGH); delay(1000); digitalWrite(PWR_PIN, LOW);
    delay(2000);
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    pinMode(LED_PIN, OUTPUT); digitalWrite(LED_PIN, HIGH);

    Wire.begin(OLED_SDA, OLED_SCK);
    if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) Serial.println("[ERRO] Falha OLED");
    updateDisplay("INICIANDO");

    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK) { delay(1000); ESP.restart(); }
    esp_now_register_recv_cb(OnDataRecv);

    pinMode(PWR_PIN, OUTPUT);
    resetModemHardware();
    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);

    mqtt.setServer(broker, mqttPort);
    mqtt.setBufferSize(1536);
}

void loop() {
    unsigned long currentMillis = millis();

    switch (currentState) {
        case MODEM_INIT:
            if (currentMillis - lastStateChange > 3000) {
                Serial.println("[LTE] Reiniciando modem via AT...");
                if (modem.restart()) {
                    modem.setNetworkMode(48);
                    modem.enableGPS();
                    currentState = WAIT_NETWORK;
                    updateDisplay("BUSCANDO REDE");
                    Serial.println("[LTE] Modem OK! Buscando rede...");
                } else {
                    retryCount++;
                    Serial.println("[LTE] Falha no restart AT.");
                    if (retryCount > 3) currentState = MODEM_ERROR;
                }
                lastStateChange = currentMillis;
            }
            break;

        case WAIT_NETWORK:
            if (currentMillis - lastStateChange > 2000) {
                if (modem.isNetworkConnected()) {
                    currentState = CONNECT_GPRS;
                    retryCount = 0;
                    Serial.println("[LTE] Achou a torre celular!");
                }
                lastStateChange = currentMillis;
            }
            if (currentMillis - lastStateChange > 60000) currentState = MODEM_ERROR;
            break;

        case CONNECT_GPRS:
            if (currentMillis - lastStateChange > 2000) {
                Serial.println("[LTE] Conectando GPRS (Internet)...");
                if (modem.gprsConnect(apn, gprsUser, gprsPass)) {
                    currentState = CONNECT_MQTT;
                    updateDisplay("GPRS OK");
                    Serial.println("[LTE] Internet conectada!");
                } else {
                    currentState = WAIT_NETWORK;
                    Serial.println("[LTE] Falha ao conectar GPRS.");
                }
                lastStateChange = currentMillis;
            }
            break;

        case CONNECT_MQTT:
            if (currentMillis - lastStateChange > 5000) {
                Serial.println("[MQTT] Conectando ao HiveMQ...");
                String clientId = "Leviata_Race_" + String(random(0xffff), HEX);
                if (mqtt.connect(clientId.c_str())) {
                    currentState = MODEM_READY;
                    retryCount = 0;
                    Serial.println("[MQTT] Conectado e pronto para envio!");
                }
                lastStateChange = currentMillis;
            }
            break;

        case MODEM_READY:
            if (currentMillis - lastStateChange > 15000) {
                if (!modem.isNetworkConnected() || !mqtt.connected()) {
                    currentState = WAIT_NETWORK;
                    Serial.println("[MQTT] Conexao perdida, voltando a buscar rede...");
                }
                lastStateChange = currentMillis;
            }
            mqtt.loop();
            break;

        case MODEM_ERROR:
            updateDisplay("ERRO CRITICO");
            Serial.println("[LTE] Entrou em Erro Critico. Resetando hardware...");
            resetModemHardware();
            currentState = MODEM_INIT;
            retryCount = 0;
            lastStateChange = currentMillis;
            break;
    }

    if (hasNewData) {
        hasNewData = false;
        v_sistema = readSystemVoltage();
        signalQuality = modem.getSignalQuality();

        const char* dispStatus = (currentState == MODEM_READY) ? "ONLINE" : "OFFLINE";
        updateDisplay(dispStatus);

        Serial.printf("\n=== PACOTE RX [%02d:%02d:%02d] ===\n", rxData.gps_h, rxData.gps_m, rxData.gps_s);
        Serial.printf("PROP : %d RPM | %0.1fA | Motor:%dC Ctrl:%dC | Erro:%d\n", rxData.motor_rpm, rxData.motor_corrente_a, rxData.motor_temp_c, rxData.ctrl_temp_c, rxData.far_falha);
        Serial.printf("ENERG: %0.1fV | Solar: %0.1fW\n", rxData.motor_v, rxData.solar_p_w);

        if (currentState == MODEM_READY) {
            if (modem.getGPS(&lat_int, &lon_int, &speed_int)) {}

            StaticJsonDocument<1536> doc;

            JsonObject solar = doc.createNestedObject("solar");
            solar["tensao"] = rxData.solar_v_v;
            solar["corrente"] = rxData.solar_i_a;
            solar["pot"] = rxData.solar_p_w;

            JsonObject bateria = doc.createNestedObject("bateria");
            bateria["soc"] = 0;
            bateria["tensao_bat"] = rxData.motor_v;
            bateria["corrente_liq"] = rxData.motor_corrente_a;

            JsonObject prop = doc.createNestedObject("prop");
            prop["rpm"] = rxData.motor_rpm;
            prop["i_motor"] = rxData.motor_corrente_a;
            prop["t_motor"] = rxData.motor_temp_c;
            prop["t_ctrl"] = rxData.ctrl_temp_c;
            prop["fardriver_falha"] = rxData.far_falha;

            JsonObject nav = doc.createNestedObject("nav");
            char timeBuf[9];
            sprintf(timeBuf, "%02d:%02d:%02d", rxData.gps_h, rxData.gps_m, rxData.gps_s);
            nav["gps_hora"] = timeBuf;
            nav["lat"] = rxData.lat; nav["lon"] = rxData.lng; nav["vel"] = rxData.vel_kmh;
            nav["gps_satelites"] = rxData.sats; nav["proa"] = rxData.gps_course; nav["hdop"] = rxData.gps_hdop;

            JsonObject nav_int = doc.createNestedObject("nav_int");
            nav_int["lat"] = lat_int; nav_int["lon"] = lon_int; nav_int["vel"] = speed_int;

            JsonObject sinal = doc.createNestedObject("sinal");
            sinal["lte"] = signalQuality;

            doc["v_sist"] = serialized(String(v_sistema, 2));

            char buffer[1536];
            size_t bytesGenerated = serializeJson(doc, buffer);

            Serial.printf("[MQTT] Publicando payload no HiveMQ (%d bytes)...\n", bytesGenerated);

            digitalWrite(LED_PIN, LOW);
            if (mqtt.publish(topic, buffer)) {
                Serial.println("[MQTT] >> PAYLOAD ENTREGUE NA NUVEM <<");
            } else {
                Serial.println("[MQTT] -- FALHA NA ENTREGA --");
            }
            digitalWrite(LED_PIN, HIGH);
        } else {
            Serial.println("[AVISO] Pacote descartado (Aguardando Conexao).");
        }
    }
}
