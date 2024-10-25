#define BLYNK_TEMPLATE_ID "TMPL2Q9gQo53J"
#define BLYNK_TEMPLATE_NAME "telemetria"
#define BLYNK_AUTH_TOKEN "gKBpE1S7RxXwAKnVnMgv0Q-VWCDXPlXa" // Token de autenticação Blynk

#include <HardwareSerial.h>
#include <WiFi.h>
#include <BlynkSimpleEsp32.h>

#define WIFI_SSID "UEA-EDU"
#define WIFI_PASSWORD "12072022"

long previousMillis = 0;    // Variável de controle do tempo
long redLedInterval = 900;  // Tempo em ms do intervalo a ser executado

//CONFIGURAÇÃO MPPT
#define RX_MPPT 34

void setup() {
  Serial.begin(115200);  // Comunicação com o PC
  Serial1.begin(19200, SERIAL_8N1, RX_MPPT, NULL); //Mudança de pino MPPT
  Serial.println("Telemetria MPPT");

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
}

void loop() {
  Blynk.run();  // Necessário para manter a conexão com o Blynk

  if (Serial1.available()) {
    String label = Serial1.readStringUntil('\t');           // leitura do label do MPPT
    String val = Serial1.readStringUntil('\r\r\n');         // leitura do valor do label

    if (label == "I") {  // Corrente da Bateria
      float corrente = val.toFloat() / 1000;  // Corrente em A
      Serial.print("Corrente da Bateria: ");
      Serial.print(corrente);
      Serial.println(" A");
      Blynk.virtualWrite(V1, corrente);  // Envia para o Blynk
    }
    else if (label == "V") {  // Tensão da Bateria
      float tensao = val.toFloat() / 1000;  // Tensão em V
      Serial.print("Tensão da bateria: ");
      Serial.print(tensao);
      Serial.println(" V");
      Blynk.virtualWrite(V0, tensao);  // Envia para o Blynk
    }
    else if (label == "VPV") {  // Tensão do Painel
      float tensaoPainel = val.toFloat() / 1000;  // Tensão em V
      Serial.print("Tensão do painel: ");
      Serial.print(tensaoPainel);
      Serial.println(" V");
      Blynk.virtualWrite(V3, tensaoPainel);  // Envia para o Blynk
    }
    else if (label == "PPV") {  // Potência do Painel
      float potencia = val.toFloat();  // Potência em W
      Serial.print("Potência do painel: ");
      Serial.print(potencia);
      Serial.println(" W");
      Blynk.virtualWrite(V2, potencia);  // Envia para o Blynk
    }
  }
}
