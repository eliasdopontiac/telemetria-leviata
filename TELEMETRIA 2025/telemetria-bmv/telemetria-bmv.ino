/*

  GPS VK2828 |  ESP32
  VCC        |  3V3
  GND        |  GND
  RX         |  D32
  TX         |  D35

  BMV        |  ESP32
  GND        |  GND
  RX         |  D34
  
*/

//BIBLIOTECAS AFINS
#include <Arduino.h>
#include <WiFi.h>
#include "VeDirectFrameHandler.h"
#include <TinyGPS.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <HardwareSerial.h>

TinyGPS gps;
VeDirectFrameHandler myve;

#define RX_GPS 32  // RX GPS
#define TX_GPS NULL // TX GPS

#define RX_BMV 34  // RX BMV

// Define os pinos para RX e TX
#define RX_PIN_3 15
#define TX_PIN_3 21

//Definições Firebase
#define WIFI_SSID "elias do pontiac"
#define WIFI_PASSWORD "morangos"

// -- Definições de Rede e Conexão MQTT / Tópicos --

const char *MQTTServer = "test.mosquitto.org";
const int MQTTPort = 1883;
const char* BMVTopic = "BMV";
const char* GPSTopic = "GPS";

// -- Instância objetos --

WiFiClient myClient;
PubSubClient client(myClient);

// -- Variáveis e constantes --

long lastMillis;
const long interval = 500;
unsigned long LastTime = 0,timestamp;
float LastVel = 0.0,velAt,deltaV, deltaT,tensao,potencia,corrente;
char payloadBMV[70],payloadGPS[50];

typedef struct GPSmqtt {
  float vel;
  float acel;
  };

typedef struct BMVmqtt {   
  float tensao;
  float corrente;
  float potencia;
  };

GPSmqtt gpsMQTT;
BMVmqtt bmvMQTT;
float Speed() {
  float velocidade;
  return velocidade = gps.f_speed_kmph();
}

float aclr()
{
  float aceleracao;
  delay(100);
  timestamp = millis(); 
  velAt = gps.f_speed_kmph(); 
  velAt = velAt * (1000.0 / 3600.0);
  LastVel = LastVel * (1000.0 / 3600.0);
  deltaV = velAt - LastVel;
  deltaT = (timestamp - LastTime) / 1000.0;
  if(deltaV>0){
      aceleracao = deltaV / deltaT;   
      LastVel = gps.f_speed_kmph(); 
      LastTime = timestamp;
    }
    return aceleracao;
}

void sendSensorData()
{
gpsMQTT.vel = Speed();
gpsMQTT.acel = aclr();
if(gpsMQTT.vel<=0) gpsMQTT.vel=0;
      for (int i = 0; i <= 3; i++){
            switch(i){
                case 1:
                Serial.println(atof(myve.veValue[i]) / 1000);
                bmvMQTT.tensao = (atof(myve.veValue[i]) / 1000);
                break;
          
                case 2:
                Serial.println(atof(myve.veValue[i]) / 1000);
                bmvMQTT.corrente = (atof(myve.veValue[i]) / 1000);
                break;
          
                case 3:
                Serial.println(atof(myve.veValue[i]) / 1000);
                bmvMQTT.potencia = (atof(myve.veValue[i]) / 1000);
                break;
                
                default:
                break;
              }
       }
       
  snprintf(
    payloadBMV, 
    sizeof(payloadBMV), 
    "{\"Tensao\":%.1f, \"Corrente\":%.1f, \"Potencia\":%.1f}", 
    bmvMQTT.tensao, bmvMQTT.corrente, bmvMQTT.potencia
    );
  client.publish(BMVTopic, payloadBMV);
  
  snprintf(payloadGPS,
  sizeof(payloadGPS),
  "{\"Velocidade\":%.1f,\"Aceleracao\":%.1f \"Corrente\":%1.f}",
  gpsMQTT.vel,gpsMQTT.acel, corrente
  );
  client.publish(GPSTopic, payloadGPS);
  Serial.printf("Dados enviados: %s\n ", payloadGPS);
  Serial.printf("Dados enviados: %s\n ", payloadBMV);
  
}

void ReadVEData()
{
  while (Serial2.available()) {
    myve.rxData(Serial2.read());
  }
}

void reconnectToBrokerMQTT()
{
  while (!client.connected()) {
    Serial.println("Conectando ao broker MQTT");
    if (client.connect("ESP32 Client")) {
      Serial.println("Conectado com sucesso!");
    } else {
      Serial.print("Falha estado: ");
      Serial.println(client.state());
      Serial.println("Tentar novamente em 5s");
      delay(5000);
    }
  }
}

void connectToBrokerMQTT()
{
  client.setServer(MQTTServer, MQTTPort);
  Serial.println("Conectado ao broker");
  delay(500);
}

void setup()
{
  Serial.begin(115200);
  Serial1.begin(9600, SERIAL_8N1, RX_GPS, TX_GPS); //Mudança de pino GPS
  Serial2.begin(19200, SERIAL_8N1, RX_BMV, NULL); //Mudança de pino BMV
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao WIFI");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  connectToBrokerMQTT();
}

void loop()
{
  if (!client.connected()) reconnectToBrokerMQTT();
  if (millis() - lastMillis >= interval) {
    sendSensorData();
    lastMillis = millis();
  }
  client.loop();
  ReadVEData();

}