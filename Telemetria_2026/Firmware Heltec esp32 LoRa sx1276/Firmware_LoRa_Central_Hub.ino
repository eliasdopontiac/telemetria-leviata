/*
 * Telemetria Leviatã 2026 - Central Hub V7 (Modo Competição)
 * Adicionado: Proa (Heading) e HDOP (Precisão GPS)
 */

#include <SPI.h>
#include <LoRa.h>
#include <TinyGPS++.h>
#include <esp_now.h>
#include <WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Wire.h>
#include <VeDirectFrameHandler.h>

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

#define GPS_RX       7
#define GPS_TX       6
#define FAR_RX       41
#define FAR_TX       42
#define MPPT_RX      39
#define MPPT_TX      38

const uint8_t CRC_TABLE_LO[] = {0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64};
const uint8_t CRC_TABLE_HI[] = {0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64};
const uint8_t FLASH_READ_ADDR[] = {0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0, 0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA};

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

struct_telemetry boatData;
uint8_t lilygoAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

TinyGPSPlus gps;
HardwareSerial serialGPS(1);
HardwareSerial serialFar(2);
HardwareSerial serialMPPT(0);
VeDirectFrameHandler mppt;
Adafruit_SSD1306 display(128, 64, &Wire, OLED_RST);

int decodeFardriverError(uint8_t* data) {
    if (data[2] & 0x01) return 1; if (data[2] & 0x02) return 2;
    if (data[2] & 0x08) return 3; if (data[2] & 0x04) return 4;
    if (data[2] & 0x10) return 5; if (data[2] & 0x40) return 7;
    if (data[2] & 0x80) return 8; if (data[3] & 0x01) return 9;
    return 0;
}

bool check_crc(uint8_t header, uint8_t* data, uint8_t* crc_bytes) {
    uint8_t a = 0x3C, b = 0x7F;
    uint8_t msg[14]; msg[0] = 0xAA; msg[1] = header; memcpy(&msg[2], data, 12);
    for(int i=0; i<14; i++) {
        uint8_t crc_i = a ^ msg[i]; a = b ^ CRC_TABLE_HI[crc_i]; b = CRC_TABLE_LO[crc_i];
    }
    return (crc_bytes[0] == a && crc_bytes[1] == b);
}

void sendKeepAlive() {
    uint8_t p[] = {0x13, 0xEC, 0x07, 0x01, 0xF1};
    uint16_t sum = 0; for(int i=0; i<5; i++) sum += p[i];
    uint8_t cs = sum & 0xFF; uint8_t not_cs = ~cs;
    uint8_t packet[] = {0xAA, p[0], p[1], p[2], p[3], p[4], cs, not_cs};
    serialFar.write(packet, 8);
}

void parseMPPT() {
    while (serialMPPT.available()) mppt.rxData(serialMPPT.read());
    for (int i = 0; i < mppt.veEnd; i++) {
        String label = String(mppt.veName[i]);
        String value = String(mppt.veValue[i]);
        if (label == "V") boatData.solar_v_v = value.toFloat() / 1000.0;
        else if (label == "I") boatData.solar_i_a = value.toFloat() / 1000.0;
        else if (label == "PPV") boatData.solar_p_w = value.toFloat();
    }
}

void setup() {
    Serial.begin(115200);
    delay(2000);

    pinMode(VEXT_PIN, OUTPUT); digitalWrite(VEXT_PIN, LOW); delay(100);

    serialGPS.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
    serialFar.begin(19200, SERIAL_8N1, FAR_RX, FAR_TX);
    serialMPPT.begin(19200, SERIAL_8N1, MPPT_RX, MPPT_TX);

    WiFi.mode(WIFI_STA);
    esp_now_init();
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, lilygoAddress, 6);
    esp_now_add_peer(&peerInfo);

    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO1);
    LoRa.begin(915E6);

    LoRa.setSpreadingFactor(10);
    LoRa.setSignalBandwidth(125E3);
    LoRa.setTxPower(20);

    Wire.begin(OLED_SDA, OLED_SCL);
    if (display.begin(SSD1306_SWITCHCAPVCC, 0x3c)) {
        display.clearDisplay(); display.display();
    }

    boatData.sync_byte = 0xAA;
}

unsigned long lastKA = 0, lastSend = 0;

void loop() {
    while (serialGPS.available()) gps.encode(serialGPS.read());
    if (gps.time.isValid()) {
        boatData.gps_h = gps.time.hour();
        boatData.gps_m = gps.time.minute();
        boatData.gps_s = gps.time.second();
    }

    if (millis() - lastKA > 1000) { sendKeepAlive(); lastKA = millis(); }
    static uint8_t farBuf[16]; static int farIdx = 0;
    while(serialFar.available()) {
        uint8_t b = serialFar.read();
        if(farIdx == 0 && b != 0xAA) continue;
        farBuf[farIdx++] = b;
        if(farIdx == 16) {
            if(check_crc(farBuf[1], &farBuf[2], &farBuf[14])) {
                uint8_t id = farBuf[1] & 0x3F;
                if(id < 55) {
                    uint8_t addr = FLASH_READ_ADDR[id];
                    if(addr == 0xE8) {
                        boatData.motor_v = ((farBuf[3]<<8)|farBuf[2])/10.0;
                        boatData.motor_corrente_a = ((farBuf[7]<<8)|farBuf[6])/4.0;
                    } else if(addr == 0xE2) {
                        int16_t rpm = (farBuf[9]<<8)|farBuf[8];
                        boatData.motor_rpm = abs(rpm) < 20 ? 0 : abs(rpm);
                        boatData.far_falha = decodeFardriverError(&farBuf[2]);
                    } else if (addr == 0xF4) {
                        boatData.motor_temp_c = ((farBuf[1] << 8) | farBuf[0]);
                    } else if (addr == 0xD6) {
                        boatData.ctrl_temp_c = ((farBuf[11] << 8) | farBuf[10]);
                    }
                }
            }
            farIdx = 0;
        }
    }

    parseMPPT();

    if (millis() - lastSend > 2500) {
        lastSend = millis();
        boatData.lat = gps.location.lat();
        boatData.lng = gps.location.lng();
        boatData.vel_kmh = gps.speed.kmph();
        boatData.sats = gps.satellites.value();

        // --- NOVOS DADOS ---
        boatData.gps_course = gps.course.isValid() ? gps.course.deg() : 0.0;
        boatData.gps_hdop = gps.hdop.isValid() ? gps.hdop.hdop() : 99.9;

        esp_now_send(lilygoAddress, (uint8_t *) &boatData, sizeof(boatData));

        LoRa.beginPacket();
        LoRa.write((uint8_t*)&boatData, sizeof(boatData));
        LoRa.endPacket();

        display.clearDisplay(); display.setCursor(0,0);
        display.setTextSize(1); display.setTextColor(WHITE);
        display.printf("  LEVIATA - RACE M\n");
        display.drawLine(0, 10, 128, 10, WHITE);

        display.setCursor(0, 15);
        display.printf("Vel: %0.1f kmh\n", boatData.vel_kmh);
        display.printf("Mot: %d RPM | %0.1fA\n", boatData.motor_rpm, boatData.motor_corrente_a);
        display.printf("Sol: %0.0f W | %0.1fA\n", boatData.solar_p_w, boatData.solar_i_a);

        if(boatData.far_falha > 0) display.printf("! ERRO FAR: %d !\n", boatData.far_falha);
        else display.printf("SYS: OK | Sat: %d\n", boatData.sats);

        display.display();
    }
}
