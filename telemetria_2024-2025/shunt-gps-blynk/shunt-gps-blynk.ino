#define BLYNK_TEMPLATE_ID "TMPL2tnLCkUUe"
#define BLYNK_TEMPLATE_NAME "eliasdopontiac"
#define BLYNK_AUTH_TOKEN "4WL7bTmYG084nujdfkvkwB4L0Q_ODJCC"  // Seu token do Blynk

#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include "Arduino.h"
#include "VeDirectFrameHandler.h"

// Defina as credenciais Wi-Fi
#define WIFI_SSID "UEA-EDU"
#define WIFI_PASSWORD "12072022"

// Pinos de comunicação VE.Direct
#define rxPin 4  // Pino RX
#define txPin 5  // Pino TX

// Instância do GPS, Serial e LCD
TinyGPSPlus gps;
HardwareSerial serialGPS(1);
LiquidCrystal_I2C lcd(0x27, 16, 2);  // Endereço I2C 0x27 e tamanho 16x2

VeDirectFrameHandler myve;

// Funções de callback e log para o VE.Direct
void HexCallback(const char* buffer, int size, void* data) {
  char tmp[100];
  if (size < 100) {
    memcpy(tmp, buffer, size * sizeof(char));
    tmp[size] = 0;
    Serial.print("received hex frame: ");
    Serial.println(tmp);
  } else {
    Serial.println("Error: buffer size too large");
  }
}

void LogHelper(const char* module, const char* error) {
  Serial.print(module);
  Serial.print(": ");
  Serial.println(error);
}

void setup() {
  Serial.begin(115200);  // Comunicação com o PC
  serialGPS.begin(9600, SERIAL_8N1, 16, 17);  // Comunicação com o NEO-6M (TX=16, RX=17)

  lcd.init();  // Inicializa o LCD
  lcd.backlight();  // Liga a luz de fundo do LCD

  lcd.setCursor(0, 0);
  lcd.print("GPS Inicializado");
  delay(2000);  // Aguardar 2 segundos para mostrar a mensagem de inicialização
  lcd.clear();

  // Conectar ao Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int timeout = 10000;  // Timeout de 10 segundos
  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Falha na conexão Wi-Fi");
    lcd.print("Wi-Fi falhou");
  } else {
    Serial.println("Conectado ao Wi-Fi");
    lcd.print("Wi-Fi conectado");
  }

  delay(2000);
  lcd.clear();

  // Inicializar Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, WIFI_SSID, WIFI_PASSWORD);

  // Inicializa a comunicação VE.Direct
  Serial1.begin(19200, SERIAL_8N1, rxPin, txPin);
}

void loop() {
  Blynk.run();  // Necessário para manter a conexão com o Blynk
  ReadVEData();  // Coleta os dados VE.Direct
  SendSensorData();  // Envia dados de GPS e VE.Direct para o Blynk
}

void ReadVEData() {
  while (Serial1.available()) {
    myve.rxData(Serial1.read());
  }
}

void SendSensorData() {
  static unsigned long prev_millis;

  // Envia dados a cada 1,5 segundo
  if (millis() - prev_millis > 1500) {
    // Coleta os dados de tensão, corrente e potência
    float tensao = atof(myve.veValue[15]) / 1000;  // Tensão em V
    float corrente = atof(myve.veValue[16]) / 1000;  // Corrente em A
    float potencia = atof(myve.veValue[17]);  // Potência em W

    // Envia dados para o Blynk
    Blynk.virtualWrite(V3, tensao);  // Tensão no Virtual Pin V3
    Blynk.virtualWrite(V4, corrente);  // Corrente no Virtual Pin V4
    Blynk.virtualWrite(V5, potencia);  // Potência no Virtual Pin V5

    // Imprime os dados no Serial Monitor
    Serial.print("Tensão (V): ");
    Serial.println(tensao);
    Serial.print("Corrente (A): ");
    Serial.println(corrente);
    Serial.print("Potência (W): ");
    Serial.println(potencia);

    // Enviar dados de GPS
    if (gps.location.isUpdated()) {
      float lat = gps.location.lat();
      float lng = gps.location.lng();
      float speed = gps.speed.kmph();  // Velocidade em km/h

      // Enviar latitude, longitude e velocidade para o Blynk
      Blynk.virtualWrite(V0, lat);
      Blynk.virtualWrite(V1, lng);
      Blynk.virtualWrite(V2, speed);

      // Imprime dados de GPS no Serial Monitor
      Serial.print("Latitude: ");
      Serial.println(lat, 4);
      Serial.print("Longitude: ");
      Serial.println(lng, 4);
      Serial.print("Velocidade (km/h): ");
      Serial.println(speed, 2);
    }

    prev_millis = millis();  // Atualiza o tempo anterior
  }
}
