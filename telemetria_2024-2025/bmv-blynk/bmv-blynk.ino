#define BLYNK_TEMPLATE_ID "TMPL2tnLCkUUe"
#define BLYNK_TEMPLATE_NAME "eliasdopontiac"
#define BLYNK_AUTH_TOKEN "E_3AYwFkf2R_KjOXDjuK9tACHxUpmfPW"  // Seu token do Blynk

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

// Instância do VE.Direct
VeDirectFrameHandler myve;

// Função de log para o VE.Direct
void LogHelper(const char* module, const char* error) {
  Serial.print(module);
  Serial.print(": ");
  Serial.println(error);
}

void setup() {
  Serial.begin(115200);  // Comunicação com o PC

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
  } else {
    Serial.println("Conectado ao Wi-Fi");
  }

  // Inicializar Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, WIFI_SSID, WIFI_PASSWORD);

  // Inicializa a comunicação VE.Direct
  Serial1.begin(19200, SERIAL_8N1, rxPin, txPin);
}

void loop() {
  Blynk.run();  // Necessário para manter a conexão com o Blynk
  ReadVEData();  // Coleta os dados VE.Direct
  SendSensorData();  // Envia dados de VE.Direct para o Blynk
}

void ReadVEData() {
  while (Serial1.available()) {
    myve.rxData(Serial1.read());  // Recebe os dados VE.Direct
  }
}

void SendSensorData() {
  static unsigned long prev_millis;

  // Envia dados a cada 1,5 segundo
  if (millis() - prev_millis > 500) {
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

    prev_millis = millis();  // Atualiza o tempo anterior
  }
}
