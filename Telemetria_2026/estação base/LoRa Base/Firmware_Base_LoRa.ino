/*
 * Telemetria Leviatã 2026 - Estação Base LoRa (Receptor)
 */

#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>

#define LORA_SCK     9
#define LORA_MISO    11
#define LORA_MOSI    10
#define LORA_SS      8
#define LORA_RST     12
#define LORA_DIO1    14

#define OLED_SDA     17
#define OLED_SCL     18
#define OLED_RST     21
#define VEXT_PIN     36

// ESTRUTURA ATUALIZADA (+ Proa e HDOP)
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
    float gps_course; // NOVO: Proa
    float gps_hdop;   // NOVO: Precisão GPS
} struct_telemetry;

struct_telemetry receivedData;

Adafruit_SSD1306 display(128, 64, &Wire, OLED_RST);

int packetsReceived = 0;
int lastRssi = 0;
float lastSnr = 0;

void setup() {
    Serial.begin(115200);

    pinMode(VEXT_PIN, OUTPUT); digitalWrite(VEXT_PIN, LOW); delay(100);

    Wire.begin(OLED_SDA, OLED_SCL);
    if (display.begin(SSD1306_SWITCHCAPVCC, 0x3c)) {
        display.clearDisplay(); display.setTextColor(WHITE); display.setTextSize(1);
        display.setCursor(0, 20); display.println("Iniciando BASE LORA..."); display.display();
    }

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO1);

    if (!LoRa.begin(915E6)) {
        display.clearDisplay(); display.setCursor(0, 0);
        display.println("Falha LoRa!"); display.display();
        while (1);
    }

    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);

    display.clearDisplay(); display.setCursor(0, 0);
    display.println("BASE LORA PRONTA"); display.display();
}

void loop() {
    int packetSize = LoRa.parsePacket();

    if (packetSize) {
        if (packetSize == sizeof(receivedData)) {
            LoRa.readBytes((uint8_t *)&receivedData, sizeof(receivedData));

            if (receivedData.sync_byte == 0xAA) {
                packetsReceived++;
                lastRssi = LoRa.packetRssi();
                lastSnr = LoRa.packetSnr();

                char timeBuf[9];
                sprintf(timeBuf, "%02d:%02d:%02d", receivedData.gps_h, receivedData.gps_m, receivedData.gps_s);

                StaticJsonDocument<1024> doc;

                JsonObject solar = doc.createNestedObject("solar");
                solar["tensao"] = receivedData.solar_v_v;
                solar["corrente"] = receivedData.solar_i_a;
                solar["pot"] = receivedData.solar_p_w;

                JsonObject bateria = doc.createNestedObject("bateria");
                bateria["soc"] = 0;
                bateria["tensao_bat"] = receivedData.motor_v;
                bateria["corrente_liq"] = receivedData.motor_corrente_a;

                JsonObject prop = doc.createNestedObject("prop");
                prop["rpm"] = receivedData.motor_rpm;
                prop["i_motor"] = receivedData.motor_corrente_a;
                prop["t_motor"] = receivedData.motor_temp_c;
                prop["t_ctrl"] = receivedData.ctrl_temp_c;
                prop["fardriver_falha"] = receivedData.far_falha;

                JsonObject nav = doc.createNestedObject("nav");
                nav["vel"] = receivedData.vel_kmh;
                nav["lat"] = receivedData.lat;
                nav["lon"] = receivedData.lng;
                nav["gps_satelites"] = receivedData.sats;
                nav["gps_hora"] = timeBuf;
                // --- INJETANDO DADOS NOVOS ---
                nav["proa"] = receivedData.gps_course;
                nav["hdop"] = receivedData.gps_hdop;

                JsonObject sinal = doc.createNestedObject("sinal");
                sinal["lora_pacotes"] = packetsReceived;
                sinal["lora"] = lastRssi;
                sinal["lte"] = 0;

                serializeJson(doc, Serial);
                Serial.println();

                display.clearDisplay(); display.setCursor(0,0);
                display.setTextSize(1); display.println("  ESTACAO BASE LORA");
                display.drawLine(0, 10, 128, 10, WHITE);

                display.setCursor(0, 15);
                display.printf("RX: %d Pkts\n", packetsReceived);
                display.printf("RSSI: %d | SNR: %0.1f\n", lastRssi, lastSnr);
                display.printf("Vel: %0.1f kmh\n", receivedData.vel_kmh);
                display.printf("Mot: %d RPM | %0.1fA\n", receivedData.motor_rpm, receivedData.motor_corrente_a);
                display.printf("Sol: %0.0f W \n", receivedData.solar_p_w);
                display.display();
            } else {
                Serial.println("{\"erro_local\":\"Pacote corrompido (Sync Byte invalido)\"}");
            }
        } else {
            Serial.printf("{\"erro_local\":\"Tamanho de pacote incompativel (Recebido: %d)\"}\n", packetSize);
        }
    }
}
