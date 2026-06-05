/*
 * Telemetria Leviata 2026 - Gateway LTE (LilyGO T-SIM7000G - FIXED)
 */

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_USE_GPRS true
#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <esp_now.h>
#include <WiFi.h>
#include <Adafruit_SSD1306.h>

#define PIN_TX 27
#define PIN_RX 26
#define PWR_PIN 4
#define BAT_ADC 35

const char apn[] = "claro.com.br";
const char* broker = "broker.hivemq.com";
const char* topic = "leviata/telemetria/race";

typedef struct __attribute__((packed)) struct_telemetry {
    uint8_t sync_byte;
    int16_t motor_rpm;
    float motor_corrente_a;
    float motor_v;
    int16_t motor_temp_c;
    int16_t ctrl_temp_c;
    uint8_t far_falha;
    float solar_p_w;
    float solar_i_a;
    float solar_v_v;
    float bateria_v; // SINCRONIZADO
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
TinyGsm modem(Serial1);
TinyGsmClient client(modem);
PubSubClient mqtt(client);
Adafruit_SSD1306 display(128, 32, &Wire, -1);

void OnDataRecv(const esp_now_recv_info *recv_info, const uint8_t *incoming, int len) {
    // DEBUG: imprimir tamanho e primeiros bytes do pacote recebido
    Serial.printf("ESP_NOW RX len=%d expected=%d\n", len, (int)sizeof(rxData));
    Serial.print("IN_BYTES: ");
    for (int i = 0; i < min(len, 12); i++) Serial.printf("%02X ", incoming[i]);
    Serial.println();

    if (len == sizeof(rxData) && incoming[0] == 0xAA) {
        memcpy(&rxData, incoming, sizeof(rxData));
        hasNewData = true;
    }
}

void setup() {
    Serial.begin(115200);
    // DEBUG: tamanho da struct para verificar packing/compatibilidade
    Serial.printf("STRUCT_SIZE=%d\n", (int)sizeof(struct_telemetry));
    WiFi.mode(WIFI_STA);
    esp_now_init();
    esp_now_register_recv_cb(OnDataRecv);
    
    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH); delay(1000); digitalWrite(PWR_PIN, LOW);
    
    Serial1.begin(115200, SERIAL_8N1, PIN_RX, PIN_TX);
    mqtt.setServer(broker, 1883);
    mqtt.setBufferSize(1536);
}

void loop() {
    if (!mqtt.connected()) {
        if (modem.restart() && modem.gprsConnect(apn, "claro", "claro")) {
            mqtt.connect("Leviata_Gateway");
        }
    }
    mqtt.loop();

    if (hasNewData) {
        hasNewData = false;
        StaticJsonDocument<1536> doc;
        
        JsonObject solar = doc.createNestedObject("solar");
        solar["tensao"] = rxData.solar_v_v;
        solar["corrente"] = rxData.solar_i_a;
        solar["pot"] = rxData.solar_p_w;

        JsonObject bateria = doc.createNestedObject("bateria");
        bateria["soc"] = 0;
        bateria["tensao_bat"] = rxData.bateria_v; // CORRETO
        bateria["corrente_liq"] = rxData.motor_corrente_a;

        JsonObject prop = doc.createNestedObject("prop");
        prop["rpm"] = rxData.motor_rpm;
        prop["i_motor"] = rxData.motor_corrente_a;
        prop["t_motor"] = rxData.motor_temp_c;
        prop["t_ctrl"] = rxData.ctrl_temp_c;
        prop["fardriver_falha"] = rxData.far_falha;

        JsonObject nav = doc.createNestedObject("nav");
        char timeBuf[9]; sprintf(timeBuf, "%02d:%02d:%02d", rxData.gps_h, rxData.gps_m, rxData.gps_s);
        nav["gps_hora"] = timeBuf;
        nav["lat"] = rxData.lat; nav["lon"] = rxData.lng; nav["vel"] = rxData.vel_kmh;
        nav["gps_satelites"] = rxData.sats; nav["proa"] = rxData.gps_course; nav["hdop"] = rxData.gps_hdop;

        char buffer[1536];
        serializeJson(doc, buffer);
        mqtt.publish(topic, buffer);
    }
}
