/**
 * PROJETO: Telemetria Veicular Unificada (Fardriver/BMV + GPS)
 * HARDWARE: Heltec WiFi LoRa 32 (V3)
 * DESCRIÇÃO: Suporta Controladora Fardriver ou Monitor BMV (Victron).
 * FIX: Utiliza Adafruit_SSD1306 para o display contornando bugs da biblioteca Heltec.
*/

#define HELTEC_POWER_BUTTON
#define HELTEC_NO_LED       // Silencia o controle interno de LED da biblioteca
#include <heltec_unofficial.h>
#include <HardwareSerial.h>
#include <TinyGPS++.h>
#include "fardriver_controller.hpp"
#include "VeDirectFrameHandler.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- SELETOR DE MODO ---
const bool MODO_FADRIVER = true; 

// --- CONFIGURAÇÕES LORA ---
#define FREQUENCY           915.0
#define BANDWIDTH           250.0
#define SPREADING_FACTOR    9
#define TRANSMIT_POWER      20
#define PAUSE               5           

// --- PINOS E HARDWARE ---
#define RX_SENSOR           41          
#define RX_GPS              7           
#define BUZZER_PIN          42          
#define V3_LED_PIN          35

// Pinos manuais do Display OLED
#define OLED_SDA            17
#define OLED_SCL            18
#define OLED_RST            21
#define VEXT_PIN            36 
const uint32_t SENSOR_TOUT  = 5000;

// Cria o objeto do display Adafruit (nomeado 'tela' para não conflitar)
Adafruit_SSD1306 tela(128, 64, &Wire, OLED_RST);

// --- ESTRUTURAS DE DADOS ---
struct __attribute__((packed)) TelemetryPacket {
  char type;             
  float lat, lon, speed;
  float volt, curr, temp, extra; 
  uint32_t uptime;
};

// --- OBJETOS ---
TinyGPSPlus gps;
FardriverData v_data;
VeDirectFrameHandler myve;
TelemetryPacket tx_pkt;

bool hasGps = false, hasSensor = false;
uint64_t last_tx = 0, last_display = 0, last_gps_upd = 0, last_sensor_upd = 0;
uint32_t pkt_cnt = 0, min_pause = 0;

// --- INTERFACE FADRIVER ---
uint32_t sw_ctrl(const uint8_t* d, uint32_t l) { return Serial2.write(d, l); }
uint32_t sr_ctrl(uint8_t* d, uint32_t l)       { return Serial2.readBytes(d, l); }
uint32_t sa_ctrl()                             { return Serial2.available(); }
FardriverSerial f_interface = {sw_ctrl, sr_ctrl, sa_ctrl};
FardriverController controller(&f_interface);

// --- AUXILIARES ---
void beep(int ms = 50) {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(ms);
  digitalWrite(BUZZER_PIN, LOW);
}

void toggleLed(bool on) {
  digitalWrite(V3_LED_PIN, on ? HIGH : LOW);
}

// --- LEITURA DE SENSORES ---
void updateSensors() {
  while (Serial1.available()) {
    if (gps.encode(Serial1.read())) {
      if (gps.location.isValid()) { hasGps = true; last_gps_upd = millis(); }
    }
  }

  if (MODO_FADRIVER) {
    if (Serial2.available() > 0) {
      controller.Read(&v_data);
      if (v_data.GetVoltage() > 1.0) { hasSensor = true; last_sensor_upd = millis(); }
    }
  } else {
    while (Serial2.available()) {
      myve.rxData(Serial2.read());
      if (strlen(myve.veValue[1]) > 0) { hasSensor = true; last_sensor_upd = millis(); }
    }
  }

  if (hasGps && (millis() - last_gps_upd > SENSOR_TOUT)) hasGps = false;
  if (hasSensor && (millis() - last_sensor_upd > SENSOR_TOUT)) hasSensor = false;
}

// --- DISPLAY ---
void drawStatus() {
  tela.clearDisplay();
  tela.setTextSize(1);
  tela.setTextColor(SSD1306_WHITE);
  
  // Cabeçalho
  tela.setCursor(0, 0);
  tela.print("TELEMETRIA: ");
  tela.println(MODO_FADRIVER ? "FDRV" : "BMV");
  tela.drawLine(0, 11, 128, 11, SSD1306_WHITE);

  // Status dos Sensores
  tela.setCursor(0, 16);
  tela.print("GPS: ");
  tela.println(hasGps ? "SINAL OK" : "BUSCANDO...");
  
  tela.setCursor(0, 28);
  tela.print("SENS:");
  tela.println(hasSensor ? "CONECTADO" : "OFFLINE");
  
  // Estatísticas de Rádio
  tela.setCursor(0, 45);
  tela.print("TX (Enviados): "); tela.println(pkt_cnt);
  
  // Barra de progresso do TX sincronizada com a regra de 1% (Duty Cycle)
  uint32_t intervalo_real = (PAUSE * 1000) > min_pause ? (PAUSE * 1000) : min_pause;
  float progress = min(1.0f, (float)(millis() - last_tx) / intervalo_real);
  
  tela.drawRect(0, 56, 128, 8, SSD1306_WHITE);
  tela.fillRect(0, 56, (int)(progress * 128), 8, SSD1306_WHITE);
  
  tela.display();
}

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  
  // 1. Inicializa a energia da tela forçadamente
  pinMode(VEXT_PIN, OUTPUT);
  digitalWrite(VEXT_PIN, LOW); 
  delay(100);

  // 2. Inicializa o I2C e a Tela Adafruit
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!tela.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Falha ao iniciar OLED");
  }
  tela.clearDisplay();
  tela.setTextSize(1);
  tela.setTextColor(SSD1306_WHITE);
  tela.setCursor(0,20);
  tela.println("Iniciando Sistema...");
  tela.display();

  // 3. Configurações de Hardware base
  pinMode(V3_LED_PIN, OUTPUT);
  digitalWrite(V3_LED_PIN, LOW);
  pinMode(BUZZER_PIN, OUTPUT);
  
  heltec_setup(); // Inicia o resto da placa (botão principal)
  
  // GPS na Serial1 e Sensores na Serial2
  Serial1.begin(9600, SERIAL_8N1, RX_GPS, -1);
  Serial2.begin(19200, SERIAL_8N1, RX_SENSOR, -1);
  
  if (MODO_FADRIVER) controller.Open();

  // 4. Inicia o LoRa (Apenas Transmissão)
  RADIOLIB_OR_HALT(radio.begin());
  radio.setFrequency(FREQUENCY);
  radio.setBandwidth(BANDWIDTH);
  radio.setSpreadingFactor(SPREADING_FACTOR);
  radio.setOutputPower(TRANSMIT_POWER);

  beep(200); 
  Serial.println("Sistema Pronto");
}

// --- LOOP ---
void loop() {
  heltec_loop();
  updateSensors();

  bool can_tx = (millis() - last_tx > (PAUSE * 1000)) && (millis() - last_tx > min_pause);
  
  if (can_tx || button.isSingleClick()) {
    tx_pkt.type   = MODO_FADRIVER ? 'F' : 'B';
    tx_pkt.lat    = hasGps ? gps.location.lat() : 0;
    tx_pkt.lon    = hasGps ? gps.location.lng() : 0;
    tx_pkt.speed  = hasGps ? gps.speed.kmph() : 0;
    tx_pkt.uptime = millis() / 1000;

    if (MODO_FADRIVER && hasSensor) {
      tx_pkt.volt = v_data.GetVoltage();
      tx_pkt.curr = v_data.GetLineCurrent();
      tx_pkt.temp = (v_data.GetMotorTemp() - 32.0) * 5.0 / 9.0;
      tx_pkt.extra = v_data.addrE2.MeasureSpeed; 
    } else if (!MODO_FADRIVER && hasSensor) {
      tx_pkt.volt = atof(myve.veValue[1]) / 1000.0;
      tx_pkt.curr = atof(myve.veValue[2]) / 1000.0;
      tx_pkt.extra = atof(myve.veValue[3]); 
      tx_pkt.temp = 0;
    }

    toggleLed(true); 
    
    uint64_t t_start = millis();
    int state = radio.transmit((uint8_t*)&tx_pkt, sizeof(tx_pkt));
    min_pause = (millis() - t_start) * 100; // Calcula limite imposto pelo rádio
    
    toggleLed(false);
    last_tx = millis(); // Reinicia o timer assim que a transmissão acabar (com ou sem sucesso)
    
    if (state == RADIOLIB_ERR_NONE) {
      pkt_cnt++;
      beep(20); 
    }
  }

  // Atualiza a tela a cada 500ms
  if (millis() - last_display > 500) {
    drawStatus();
    last_display = millis();
  }
}