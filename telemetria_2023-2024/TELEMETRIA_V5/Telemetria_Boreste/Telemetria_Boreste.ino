/*
CONEXÕES COM MPPT:
  MPPT   -     ESP pin
  GND    -     GND
  RX     -     -
  TX     -     D34
  Power        -
*/
//
long previousMillis = 0;    // Variável de controle do tempo
long redLedInterval = 900;  // Tempo em ms do intervalo a ser executado
long lastMsg = 0;

//CONFIGURAÇÃO MPPT
byte len = 5;
int intmeetwaarde;
String label, val;
float meetwaarde;
char buf[45];
char correntebateria[6];
char potenciapainel[6];
char rendimentoontem[6];
char potenciamaximaontem[6];
char rendimentohoje[6];
char tensaopainel[6];
char tensaobateria[6];
char correntepainel[12];

float correntebateria2;
float potenciapainel1;
float tensaopainel1;
float tensaobateria1;

#include <HardwareSerial.h>

//CONFIGURAÇÃO CAN
#include <SPI.h>
#include <mcp2515.h>
#define CS 2
#include "EmonLib.h"
#include <esp_now.h>
#include <WiFi.h>

uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

struct can_frame canMsg;
struct can_frame canMsg2;
struct can_frame canMsg3;

#define RX_MPPT 34
EnergyMonitor emon1;
MCP2515 mcp2515(CS);

typedef struct struct_message {
  float a;
  float b;
  float c;
  float d;
} 
struct_message;
struct_message myData;
esp_now_peer_info_t peerInfo;

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void setup() {
  Serial.begin(115200);

  while (!Serial);
  Serial1.begin(19200, SERIAL_8N1, RX_MPPT, NULL); //Mudança de pino MPPT
  Serial.println("Telemetria MPPT");
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_send_cb(OnDataSent);
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
}

void loop() {

  if (Serial1.available()) {

    label = Serial1.readStringUntil('\t');           // leitura do label do MPPT
    val = Serial1.readStringUntil('\r\r\n');         // leitura do valor do label

    if (label == "I")                                // Escolha dos parametros do MPPT. Verificar no datasheet da victron para todos dos labels.
    {                                                
      val.toCharArray(buf, sizeof(buf));             // conversão do valor para array.
      float meetwaarde = atoi(buf);                  // conversão para float
      meetwaarde = meetwaarde / 1000;                // ajustando para o valor correto, por padrão virá na escala de milis.
      dtostrf(meetwaarde, len, 2, correntebateria);  // Conversão do valor calculado para string value to string
      correntebateria[len] = ' ';
      correntebateria[len + 1] = 0;
      Serial.print("Corrente da Bateria: ");
      float correntebateria1;
      correntebateria1 = atof(correntebateria);
      correntebateria2 = (correntebateria1 * 10);
      Serial.print(correntebateria2);
      Serial.println("A");
    }

    else if (label == "V")  //TENSÃO DA BATERIA
    {
      val.toCharArray(buf, sizeof(buf));
      float meetwaarde = atoi(buf);
      meetwaarde = meetwaarde / 1000;
      dtostrf(meetwaarde, len, 2, tensaobateria);
      tensaobateria[len] = ' ';
      tensaobateria[len + 1] = 0;
      Serial.print("Tensão da bateria: ");
      tensaobateria1 = atof(tensaobateria);
      Serial.print(tensaobateria1);
      Serial.println("V");
    }

    else if (label == "VPV")  //TENSÃO DO PAINEL
    {
      val.toCharArray(buf, sizeof(buf));
      float meetwaarde = atoi(buf);
      meetwaarde = meetwaarde / 1000;
      dtostrf(meetwaarde, len, 2, tensaopainel);
      tensaopainel[len] = ' ';
      tensaopainel[len + 1] = 0;
      tensaopainel1 = atof(tensaopainel);
      Serial.print("Tensão do painel: ");
      Serial.print(tensaopainel1);
      Serial.println("V");
    }


    else if (label == "PPV")  //POTENCIA PAINEL
    {
      val.toCharArray(buf, sizeof(buf));
      meetwaarde = atoi(buf);
      dtostrf(meetwaarde, len, 0, potenciapainel);
      potenciapainel[len] = ' ';
      potenciapainel[len + 1] = 0;
      Serial.print("Potencia do painel: ");
      potenciapainel1 = atof(potenciapainel);
      Serial.print(potenciapainel1);
      Serial.println("W");
    }

  }

    myData.a = potenciapainel1;
    myData.b = tensaopainel1;
    myData.c = tensaobateria1;
    myData.d = correntebateria2;
    
   static unsigned long prev_millis;
  if (millis() - prev_millis > 1000) {
    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
    prev_millis = millis();
    Serial.println("Sent with success");
  }
  
  }
