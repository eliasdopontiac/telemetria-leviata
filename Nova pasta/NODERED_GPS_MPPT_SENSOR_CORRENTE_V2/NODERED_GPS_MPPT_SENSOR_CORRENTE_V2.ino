/*
ESP32           PERIFERICOS
GND             GNG(GPS, LORA, CAN, MPPT, HALL)
VDD             VCC(CAN), 
D2              DIO0(LORA)
D12             RST(LORA)
D19             MISO(LORA)
D5              NSS(LORA)
D23             MOSI(LORA), SI(CAN)
D18             SCLK(D18), SCK(CAN)
D19             SO(CAN)
D15             INT(CAN)
D35             A0(HALL)
RX0             T(GPS)
TX0             R(GPS)
RX2             TX(MPPT)


// VOLTÍMETRO (VN,GND)
*/

#include <TinyGPS.h>                   // Biblioteca de GPS
#include "EmonLib.h"                   // Biblioteca de corrente
#include <SPI.h>                       // Biblioteca de Integração dos componentes
#include <WiFi.h>                      // Biblioteca de WiFi
#include <PubSubClient.h>              // Biblioteca de envios de dados MQTT

// GPS
TinyGPS gps;                           
String LATITUDE;
String LONGITUDE;
int DEG;
int MIN1;
int MIN2;

// MPPT
EnergyMonitor emon1;
char correntebateria[6];
char potenciapainel[6];
char rendimentoontem[6];
char potenciamaximaontem[6];
char rendimentohoje[6];
char tensaopainel[6];
char tensaobateria[6];
char correntepainel[12];
long lat; long lon; unsigned long fix_age;
long redLedInterval = 900;  // Tempo em ms do intervalo a ser executado
long lastMsg = 0;
int correntebateria2;
int potenciapainel1;
int tensaopainel1;
int tensaobateria1;
float current = 0.00;
int count = 0;

// Wi-Fi
const char* ssid = "LEVIATÃ_UEA_23";
const char* password = "PORAQUE_23";
const char* mqtt_server = "test.mosquitto.org";
WiFiClient leviata;
PubSubClient client(leviata);

const int led = 2;

char char_gps[25];
String gps_str;

char char_corrente[5];
String corentesaida_str;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");

  Serial.print(",mensagem: ");
  String messageInfo;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageInfo += (char)message[i];
  }
  Serial.println();

  if (topic == "room/light") {
    Serial.print("Mudando a luz para ");
    if (messageInfo == "on") {
      digitalWrite(led, HIGH);
      Serial.println("On");
    } else if (messageInfo == "off") {
      digitalWrite(led, LOW);
      Serial.println("Off");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("leviata")) {
      Serial.println("connectado");
      client.subscribe("room/light");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(1000);
    }
  }
}

void LAT() {
  DEG = lat / 1000000;
  MIN1 = (lat / 10000) % 100;
  MIN2 = lat % 10000;
  LATITUDE = String(lat);
}

void LON() {
  DEG = lon / 1000000;
  MIN1 = (lon / 10000) % 100;
  MIN2 = lon % 10000;
}

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  emon1.current(35, 14);
  while (!Serial);
  Serial1.begin(19200, SERIAL_8N1, 16, 17);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  while (Serial.available()) {
    int C = Serial.read();
    if (gps.encode(C)) {}
  }

  //long lat;long lon;long fix_age;
  gps.get_position(&lat, &lon, &fix_age);
  unsigned long currentMillis = millis();

  if (Serial1.available()) {
    String label = Serial1.readStringUntil('\t');
    String val = Serial1.readStringUntil('\r\r\n');

    if (label == "I") {
      float meetwaarde = val.toFloat() / 1000;
      dtostrf(meetwaarde, 5, 1, correntebateria);
      correntebateria2 = (meetwaarde * 10);
      Serial.print("Corrente da Bateria: ");
      Serial.print(correntebateria2);
      Serial.println("A");
      client.publish("Current_Input", correntebateria);
    } else if (label == "V") {
      float meetwaarde = val.toFloat() / 1000;
      dtostrf(meetwaarde, 5, 1, tensaobateria);
      tensaobateria1 = meetwaarde;
      Serial.print("Tensão da bateria: ");
      Serial.print(tensaobateria1);
      Serial.println("V");
      client.publish("PBattery_Voltage", tensaobateria);
    } else if (label == "VPV") {
      float meetwaarde = val.toFloat() / 1000;
      dtostrf(meetwaarde, 5, 1, tensaopainel);
      tensaopainel1 = meetwaarde;
      Serial.print("Tensão do painel: ");
      Serial.print(tensaopainel1);
      Serial.println("V");
    } else if (label == "PPV") {
      float meetwaarde = val.toFloat();
      dtostrf(meetwaarde, 5, 0, potenciapainel);
      potenciapainel1 = meetwaarde;
      Serial.print("Potencia do painel: ");
      Serial.print(potenciapainel1);
      Serial.println("W");
      client.publish("Power_Input", potenciapainel);
    }

    unsigned long now = millis();
    if (now - lastMsg > 10) {
      lastMsg = now;
      LAT();
      LON();
      gps.get_position(&lat, &lon, &fix_age);

      double Irms = emon1.calcIrms(1480);
      current = (Irms / 2.6) + 2.643;

      gps_str = String(lat) + String(lon);
      gps_str.toCharArray(char_gps, 25);

      corentesaida_str = String(current);
      corentesaida_str.toCharArray(char_corrente, 5);

      client.publish("gps", char_gps);
      client.publish("PCurrent_Output", char_corrente);
    }
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}