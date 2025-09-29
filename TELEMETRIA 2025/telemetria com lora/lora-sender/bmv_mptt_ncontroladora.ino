// Rascunho unificado: 3 UARTs para leitura + LoRa + OLED para logs
#include "VeDirectFrameHandler.h"
#include <HardwareSerial.h>
#include <TinyGPS++.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "fardriver_controller.hpp"

// --- SELETOR DE DISPOSITIVO NA SERIAL (UART0) ---
// Defina como 'true' para usar a controladora Fardriver
// Defina como 'false' para usar o BMV
const bool USE_FADRIVER_OR_BMV = true;

// --- VE.Direct (BMV) ---
VeDirectFrameHandler myve;
#define RX_BMV 36   // Pino RX para a Serial (UART0)
const int BMV_BAUD_RATE = 19200;

// --- GPS NEO 6M ---
TinyGPSPlus gps;
#define RX_GPS 13   // Pino RX para a Serial1 (UART1)
const int GPS_BAUD_RATE = 9600;

// --- LoRa ---
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26
#define BAND 915E6
unsigned int counter = 0;

// --- OLED SSD1306 ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_SDA 4
#define OLED_SCL 15
#define OLED_RST 16
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST);

// --- Buzzer ---
#define BUZZER_PIN 23 // Pino para o buzzer
#define BUZZER_CHANNEL 0
#define BUZZER_FREQ 2000
#define BUZZER_RESOLUTION 8

// --- Estruturas de dados para envio via LoRa ---
// Estas estruturas devem ser idênticas no recetor para a descodificação correta.
// Pacote para o modo BMV
typedef struct {
  float bmv_T;
  float bmv_I;
  float bmv_P;
  float gps_lat;
  float gps_lon;
  float gps_speed_kmh;
} BmvPacket;

// Pacote para o modo Fardriver
typedef struct {
  float gps_lat;
  float gps_lon;
  float gps_speed_nos;
  float ctrl_volt;
  float ctrl_line_current;
  float ctrl_motor_temp_c;
  float ctrl_rpm; // RPM foi adicionado aqui
} FardriverPacket;

// --- Dados ---
float BMV_T = 0, BMV_I = 0, BMV_P = 0;
float GPS_lat = 0, GPS_lon = 0;
float GPS_speed_kmh = 0;

// Estrutura de dados da controladora (fardriver) da biblioteca
FardriverData my_vehicle_data;

// --- Controle de tempo ---
unsigned long lastUpdate = 0;
const unsigned long updateInterval = 1000;
unsigned long lastLoRaSend = 0;
const unsigned long loraSendInterval = 2000;
int displayPage = 0; // 0: Fardriver/BMV, 1: GPS, 2: LoRa

// --- Protótipos ---
void oledLog(const char* msg);
void updateDisplay();
void parseBMV();
void parseGPS();
void controllerLoop();
void sendLoRaPacket();
void beep();

// ---------------------------------------------------
// Implementação das funções de interface para fardriver
// A porta Serial (UART0) será usada para a controladora ou o BMV.
// ---------------------------------------------------
uint32_t serial_write_ctrl(const uint8_t* data, uint32_t length) {
  if (USE_FADRIVER_OR_BMV) {
    return Serial.write(data, length);
  }
  return 0;
}
uint32_t serial_read_ctrl(uint8_t* data, uint32_t length) {
  if (USE_FADRIVER_OR_BMV) {
    return Serial.readBytes(data, length);
  }
  return 0;
}
uint32_t serial_available_ctrl() {
  if (USE_FADRIVER_OR_BMV) {
    return Serial.available();
  }
  return 0;
}

// Registrar a interface
FardriverSerial my_serial_interface = {serial_write_ctrl, serial_read_ctrl, serial_available_ctrl};
FardriverController controller(&my_serial_interface);

// ---------------------------------------------------
// Funções de log para o OLED
// ---------------------------------------------------
void oledLog(const char* msg) {
  display.clearDisplay();
  display.setCursor(0,0);
  display.println(msg);
  display.display();
}

// ---------------------------------------------------
// Analisar o BMV (VE.Direct)
// ---------------------------------------------------
void parseBMV() {
  while (Serial.available()) {
    myve.rxData(Serial.read());
  }
}
bool hasValidBMVData() {
  for (int i = 1; i <= 3; i++) {
    if (strlen(myve.veValue[i]) == 0) return false;
    if (atof(myve.veValue[i]) == 0.0) return false;
  }
  return true;
}
void parseBMV_values_from_myve() {
  if (strlen(myve.veValue[1]) > 0) BMV_T = atof(myve.veValue[1]) / 1000.0;
  if (strlen(myve.veValue[2]) > 0) BMV_I = atof(myve.veValue[2]) / 1000.0;
  if (strlen(myve.veValue[3]) > 0) BMV_P = atof(myve.veValue[3]) / 1000.0;
}

// ---------------------------------------------------
// Analisar o GPS
// ---------------------------------------------------
void parseGPS() {
  while (Serial1.available()) {
    gps.encode(Serial1.read());
  }
  if (gps.location.isUpdated()) {
    GPS_lat = gps.location.lat();
    GPS_lon = gps.location.lng();
  }
  if (gps.speed.isUpdated()) {
    GPS_speed_kmh = gps.speed.kmph();
  }
}

// ---------------------------------------------------
// Loop do controlador (fardriver)
// ---------------------------------------------------
unsigned long lastControllerAttempt = 0;
const unsigned long controllerPollInterval = 1000; // ms
void controllerLoop() {
  if (millis() - lastControllerAttempt < controllerPollInterval) return;
  lastControllerAttempt = millis();
  if (serial_available_ctrl() > 0) {
    controller.Read(&my_vehicle_data);
  }
}

// ---------------------------------------------------
// Função para emitir um bipe curto
// ---------------------------------------------------
void beep() {
  ledcWrite(BUZZER_CHANNEL, 128); // 50% de duty cycle
  delay(50);
  ledcWrite(BUZZER_CHANNEL, 0);
}

// ---------------------------------------------------
// Função para enviar pacote LoRa
// ---------------------------------------------------
void sendLoRaPacket() {
  LoRa.beginPacket();
  
  if (USE_FADRIVER_OR_BMV) {
    // Envia o pacote da Controladora
    FardriverPacket data;
    data.gps_lat = GPS_lat;
    data.gps_lon = GPS_lon;
    data.gps_speed_nos = GPS_speed_kmh / 1.852; // conversão de km/h para nó
    data.ctrl_volt = my_vehicle_data.GetVoltage();
    data.ctrl_line_current = my_vehicle_data.GetLineCurrent();
    data.ctrl_motor_temp_c = (my_vehicle_data.GetMotorTemp() - 32.0) * 5.0 / 9.0;
    
    // Pega o RPM do campo correto da estrutura
    data.ctrl_rpm = my_vehicle_data.addrE2.MeasureSpeed;
    
    LoRa.write('F'); // Flag para o recetor identificar o pacote
    LoRa.write((uint8_t*)&data, sizeof(data));
  } else {
    // Envia o pacote do BMV
    BmvPacket data;
    data.bmv_T = BMV_T;
    data.bmv_I = BMV_I;
    data.bmv_P = BMV_P;
    data.gps_lat = GPS_lat;
    data.gps_lon = GPS_lon;
    data.gps_speed_kmh = GPS_speed_kmh;

    LoRa.write('B'); // Flag para o recetor identificar o pacote
    LoRa.write((uint8_t*)&data, sizeof(data));
  }
  
  LoRa.endPacket();
  counter++;

  // Emitir bipe para indicar envio
  beep();
}

// ---------------------------------------------------
// Função para atualizar o display OLED
// ---------------------------------------------------
void updateDisplay() {
  display.clearDisplay();
  display.setCursor(0,0);
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  
  displayPage = (displayPage + 1) % 3;

  if (displayPage == 0) {
    display.println("Dados Bateria:");
    if (USE_FADRIVER_OR_BMV) {
      display.print("CTRL V: "); display.println(my_vehicle_data.GetVoltage());
      display.print("CTRL I: "); display.println(my_vehicle_data.GetLineCurrent());
      display.print("RPM: "); display.println(my_vehicle_data.addrE2.MeasureSpeed);
    } else {
      display.print("BMV V: "); display.println(BMV_T);
      display.print("BMV I: "); display.println(BMV_I);
    }
  } else if (displayPage == 1) {
    display.println("GPS:");
    display.print("Lat: "); display.println(GPS_lat, 6);
    display.print("Lon: "); display.println(GPS_lon, 6);
    display.print("Vel: "); display.print(GPS_speed_kmh); display.println(" km/h");
  } else if (displayPage == 2) {
    display.println("LoRa Status:");
    display.print("Pacotes enviados:");
    display.println(counter);
    display.print("Frequencia:");
    display.println(BAND / 1E6);
  }
  
  display.display();
}

// ---------------------------------------------------
// Configuração (setup)
// ---------------------------------------------------
void setup() {
  // Inicializa o OLED
  Wire.begin(OLED_SDA, OLED_SCL);
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for(;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("Iniciando...");
  display.display();

  // Inicializa LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  if (!LoRa.begin(BAND)) {
    oledLog("Falha LoRa!");
    for(;;);
  }
  // Configurações do LoRa
  LoRa.setTxPower(20);
  LoRa.setSpreadingFactor(12);

  oledLog("LoRa OK!");

  // Configura o buzzer
  ledcSetup(BUZZER_CHANNEL, BUZZER_FREQ, BUZZER_RESOLUTION);
  ledcAttachPin(BUZZER_PIN, BUZZER_CHANNEL);
  
  // Inicializa as três UARTs
  // O pino de RX da Serial0 (UART0) será 36
  Serial.begin(19200, SERIAL_8N1, RX_BMV, -1);

  // O pino de RX da Serial1 (UART1) será 13
  Serial1.begin(GPS_BAUD_RATE, SERIAL_8N1, RX_GPS, -1);

  // A Serial2 não é utilizada
  
  if (USE_FADRIVER_OR_BMV) {
    controller.Open();
  } else {
    oledLog("Aguardando BMV...");
    unsigned long start = millis();
    while (!hasValidBMVData() && (millis() - start < 5000)) {
      parseBMV();
      delay(10);
    }
    if (hasValidBMVData()) {
      oledLog("BMV conectado!");
      parseBMV_values_from_myve();
    } else {
      oledLog("BMV: sem dados validos");
    }
  }
}

// ---------------------------------------------------
// Loop principal (não-bloqueante)
// ---------------------------------------------------
void loop() {
  unsigned long now = millis();

  if (USE_FADRIVER_OR_BMV) {
    controllerLoop();
  } else {
    parseBMV();
    if (hasValidBMVData()) {
      parseBMV_values_from_myve();
    }
  }

  parseGPS();
  
  if (now - lastUpdate >= updateInterval) {
    lastUpdate = now;
    updateDisplay();
  }

  if (now - lastLoRaSend >= loraSendInterval) {
    lastLoRaSend = now;
    sendLoRaPacket();
  }
}
