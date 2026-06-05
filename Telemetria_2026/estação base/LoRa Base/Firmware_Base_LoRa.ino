/*
 * Telemetria Leviata 2026 - Estacao Base LoRa (Receptor - FIXED)
 * Hardware: TTGO/Heltec V2 (ESP32 Classico + LoRa SX1276)
 */

#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>

#define SCK     5
#define MISO    19
#define MOSI    27
#define SS      18
#define RST     14
#define DIO0    26

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
    float bateria_v; // CAMPO SINCRONIZADO
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

struct_telemetry receivedData;
int packetsReceived = 0;

void setup() {
    Serial.begin(115200);
    // DEBUG: tamanho da struct para verificar packing/compatibilidade
    Serial.printf("STRUCT_SIZE=%d\n", (int)sizeof(struct_telemetry));
    SPI.begin(SCK, MISO, MOSI, SS);
    LoRa.setPins(SS, RST, DIO0);

    if (!LoRa.begin(915E6)) {
        Serial.println("{\"erro_local\":\"Falha LoRa\"}");
        while (1);
    }
    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
}

void loop() {
    int packetSize = LoRa.parsePacket();
    if (packetSize == sizeof(receivedData)) {
        LoRa.readBytes((uint8_t *)&receivedData, sizeof(receivedData));
        // DEBUG: imprimir primeiros bytes recebidos para validar packing
        uint8_t *p = (uint8_t *)&receivedData;
        Serial.print("IN_BYTES: ");
        for (int i = 0; i < min((int)sizeof(receivedData), 12); i++) Serial.printf("%02X ", p[i]);
        Serial.println();

        if (receivedData.sync_byte == 0xAA) {
            packetsReceived++;
            char timeBuf[9];
            sprintf(timeBuf, "%02d:%02d:%02d", receivedData.gps_h, receivedData.gps_m, receivedData.gps_s);

            StaticJsonDocument<1024> doc;
            JsonObject solar = doc.createNestedObject("solar");
            solar["tensao"] = receivedData.solar_v_v;
            solar["corrente"] = receivedData.solar_i_a;
            solar["pot"] = receivedData.solar_p_w;

            JsonObject bateria = doc.createNestedObject("bateria");
            bateria["soc"] = 0;
            bateria["tensao_bat"] = receivedData.bateria_v; // CORRETO: Tensao real
            bateria["corrente_liq"] = receivedData.motor_corrente_a;

            JsonObject prop = doc.createNestedObject("prop");
            prop["rpm"] = receivedData.motor_rpm;
            prop["i_motor"] = receivedData.motor_corrente_a;
            prop["t_motor"] = receivedData.motor_temp_c;
            prop["t_ctrl"] = receivedData.ctrl_temp_c;
            prop["fardriver_falha"] = receivedData.far_falha;

            JsonObject nav = doc.createNestedObject("nav");
            nav["vel"] = receivedData.vel_kmh;
            nav["lat"] = receivedData.lat; nav["lon"] = receivedData.lng;
            nav["gps_satelites"] = receivedData.sats; nav["gps_hora"] = timeBuf;
            nav["proa"] = receivedData.gps_course; nav["hdop"] = receivedData.gps_hdop;

            JsonObject sinal = doc.createNestedObject("sinal");
            sinal["lora_pacotes"] = packetsReceived;
            sinal["lora"] = LoRa.packetRssi();

            serializeJson(doc, Serial);
            Serial.println();
        }
    }
}
