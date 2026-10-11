/*
  =============================================================================
  TELEMETRIA LEVIATÃ 2026 - SIMULADOR DA ESTAÇÃO BASE LORA (SERIAL USB)
  =============================================================================
  Hardware: ESP32 Classico / Heltec v2/v3 / TTGO LoRa / NodeMCU-32S
  Baud Rate: 115200 bps
  Biblioteca recomendada: ArduinoJson (v6 ou v7)
  
  Este código faz qualquer ESP32 conectado via USB simular EXATAMENTE a saída 
  Serial da Estação Base LoRa real (Firmware_Base_LoRa.ino), gerando as mesmas 
  estruturas JSON que a base real envia após receber um pacote de rádio do barco.
  
  ESTRUTURA JSON GERADA (Sincronizada com Firmware_Base_LoRa.ino):
  {
    "solar":   { "tensao": 48.5, "corrente": 6.2, "pot": 300.7 },
    "bateria": { "soc": 88.5, "tensao_bat": 51.8, "corrente_liq": -12.3 },
    "prop":    { "rpm": 1420, "i_motor": 18.5, "t_motor": 48, "t_ctrl": 39, "fardriver_falha": 0 },
    "nav":     { "vel": 18.4, "lat": -22.41548, "lon": -41.81782, "proa": 120.5, "gps_satelites": 12, "gps_hora": "18:45:00", "hdop": 0.8 },
    "sinal":   { "lora_pacotes": 142, "lora": -78 }
  }
  
  COMANDOS VIA SERIAL MONITOR (Para testes de diagnóstico na pista):
  - FAULT:1  -> Simula Sobretensão na Bateria
  - FAULT:4  -> Simula Superaquecimento do Motor (>85°C)
  - FAULT:7  -> Simula Falha no Acelerador (Throttle)
  - CLEAR    -> Limpa falhas (fardriver_falha = 0)
  =============================================================================
*/

#include <Arduino.h>
#define ARDUINOJSON_USE_DOUBLE 1
#include <ArduinoJson.h>
#include <math.h>

unsigned long lastPacketTime = 0;
const unsigned long PACKET_INTERVAL = 1000; // 1Hz (1 pacote por segundo)

int packetsReceived = 0;
int farFalha = 0;

float socSim = 92.5;
float angleSim = 0.0;

// Coordenadas da Lagoa de Imboassica (Macaé - RJ)
const double LAT_BASE = -22.41548354710283;
const double LON_BASE = -41.81782266355955;

void setup() {
  Serial.begin(115200);
  delay(1000);
}

void processCommands() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toUpperCase();

    if (input.startsWith("FAULT:")) {
      farFalha = input.substring(6).toInt();
    } else if (input == "CLEAR" || input == "0") {
      farFalha = 0;
    }
  }
}

void loop() {
  processCommands();

  unsigned long now = millis();
  if (now - lastPacketTime >= PACKET_INTERVAL) {
    lastPacketTime = now;
    packetsReceived++;

    // 1. Variação suave de navegação (Curva senoidal)
    angleSim += 0.08;
    if (angleSim > 2 * M_PI) angleSim = 0;

    float velKmh = 12.0 + 8.0 * sin(angleSim);
    if (velKmh < 0) velKmh = 0;

    int rpm = 1000 + (int)(800.0 * (velKmh / 20.0));
    float iMotor = 5.0 + 22.0 * (velKmh / 20.0);

    // 2. Sistema Solar e Bateria
    float vSolar = 47.5 + 2.0 * cos(angleSim * 0.5);
    float iSolar = 4.0 + 3.5 * sin(angleSim * 0.4);
    if (iSolar < 0) iSolar = 0;
    float pSolar = vSolar * iSolar;

    socSim -= 0.015; // Descarrega suavemente
    if (socSim < 10.0) socSim = 95.0;

    float vBat = 48.0 + (socSim / 100.0) * 5.0;
    float iLiq = (pSolar / vBat) - iMotor;

    // 3. Temperaturas (Fardriver e Motor)
    int tMotor = (farFalha == 4) ? 89 : (40 + (int)(15.0 * (velKmh / 20.0)));
    int tCtrl = 35 + (int)(10.0 * (velKmh / 20.0));

    // 4. GPS & Relógio (Trajetória de raia na Lagoa de Imboassica em torno do Home)
    // Home: -22.41548354710283, -41.81782266355955
    double dLat = 0.00085 * sin(angleSim);
    double dLon = 0.00140 * cos(angleSim);
    double lat = LAT_BASE + dLat;
    double lon = LON_BASE + dLon;

    // Proa tangencial (direção exata de deslocamento do barco em graus náuticos 0-360°)
    double dLatDt = 0.00085 * cos(angleSim);
    double dLonDt = -0.00140 * sin(angleSim);
    float proa = fmod((atan2(dLonDt, dLatDt) * (180.0 / M_PI) + 360.0), 360.0);

    unsigned long totalSec = now / 1000;
    int h = (15 + (totalSec / 3600)) % 24;
    int m = (totalSec / 60) % 60;
    int s = totalSec % 60;
    char timeBuf[9];
    sprintf(timeBuf, "%02d:%02d:%02d", h, m, s);

    // 5. Sinal LoRa RSSI
    int rssi = -70 - (rand() % 20); // -70 a -90 dBm

    // 6. Construção do JSON usando ArduinoJson (Idêntico ao Firmware_Base_LoRa.ino)
    StaticJsonDocument<1024> doc;

    JsonObject solar = doc.createNestedObject("solar");
    solar["tensao"] = serialized(String(vSolar, 1));
    solar["corrente"] = serialized(String(iSolar, 1));
    solar["pot"] = serialized(String(pSolar, 0));

    JsonObject bateria = doc.createNestedObject("bateria");
    bateria["soc"] = serialized(String(socSim, 1));
    bateria["tensao_bat"] = serialized(String(vBat, 1));
    bateria["corrente_liq"] = serialized(String(iLiq, 1));

    JsonObject prop = doc.createNestedObject("prop");
    prop["rpm"] = rpm;
    prop["i_motor"] = serialized(String(iMotor, 1));
    prop["t_motor"] = tMotor;
    prop["t_ctrl"] = tCtrl;
    prop["fardriver_falha"] = farFalha;

    JsonObject nav = doc.createNestedObject("nav");
    nav["vel"] = serialized(String(velKmh, 1));
    nav["lat"] = serialized(String(lat, 7)); // 7 casas decimais para precisão total
    nav["lon"] = serialized(String(lon, 7));
    nav["gps_satelites"] = 12;
    nav["gps_hora"] = timeBuf;
    nav["proa"] = serialized(String(proa, 1));
    nav["hdop"] = 0.8;

    JsonObject sinal = doc.createNestedObject("sinal");
    sinal["lora_pacotes"] = packetsReceived;
    sinal["lora"] = rssi;

    // Saída idêntica ao Firmware_Base_LoRa.ino
    serializeJson(doc, Serial);
    Serial.println();
  }
}
