
/*
MCP 2515    ESP32       LORA sx1278   GPS
GND         GND         GND           G
VCC         VDD(3V3)    VCC           V
-           D2          DIO0          -
-           D12         RST           -
-           D19         MISO          -
-           D5          NSS           -
SI          D23         MOSI          -
SCK         D18         SCLK          -
SO          D19         -             -
INT         D15         -             -
-           RX0         -             T
-           TX0         -             R

// VOLTÍMETRO (VN,GND)
*/


//GPS
unsigned long previousMillis = 0;
const long intervalo = 100;
#include <TinyGPS.h>
//#include <Wire.h>
TinyGPS gps;

String LATITUDE;
String LONGITUDE;

long lat;
long lon;
unsigned long fix_age;
int DEG;
int MIN1;
int MIN2;
int C;

//CAN
#include <SPI.h>
#include <mcp2515.h>
#define CS 5
struct can_frame canMsg;
MCP2515 mcp2515(CS);
String x;
String y;
String l;
String m;
String n;
String o;

String A;


//  WI-FI
#include <WiFi.h>
#include <PubSubClient.h>
const char* ssid = "LEVIATÃ_UEA_23";
const char* password = "PORAQUE_23";
const char* mqtt_server = "test.mosquitto.org";
WiFiClient leviata;
PubSubClient client(leviata);

const int led = 2;
char char_x[3];
char char_y[3];
char char_l[5];
char char_m[3];

char char_gps[25];
String gps_str;
String l_str;
String m_str;
String x_str;
String y_str;

long lastMsg = 0;

void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
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



  // Ligando Led com o topico declarado
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
      // Wait 5 seconds before retrying
      delay(1000);
    }
  }
}

//------------------------------------------------------------------------------------------------------------------
void LAT() {
  DEG = lat / 1000000;
  MIN1 = (lat / 10000) % 100;
  MIN2 = lat % 10000;
  //Serial.print("LAT:");
  //Serial.println(lat);
  LATITUDE = String(lat);
}
void LON() {
  DEG = lon / 1000000;
  MIN1 = (lon / 10000) % 100;
  MIN2 = lon % 10000;
  //Serial.print("LON:");
  //Serial.println(lon);
  //Serial.print(String(lon));
}
//----------------------------------------------------------------------------------------------------------------------------


void setup() {
  pinMode(led, OUTPUT);  // Initialize the BUILTIN_LED pin as an output
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  //CAN
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  Serial.println("------- CAN Read ----------");
}

void loop() {

while (Serial.available()){
  C = Serial.read(); 
  if (gps.encode(C)){}
 }
 gps.get_position(&lat, &lon, &fix_age);
 unsigned long currentMillis = millis();    //Tempo atual em ms

  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id == 36) {

      Serial.print("POTENCIA DO PAINEL MPPT: ");
      l = String(canMsg.data[0]);
      Serial.print(l);
      Serial.println("W");

      Serial.print("TENSÃO PAINEL MPPT: ");
      m = String(canMsg.data[1]);
      Serial.print(m);
      Serial.println("Vp");

      Serial.print("TENSÃO DA BATERIA MPPT: ");
      y = String(canMsg.data[2]);
      Serial.print(y);
      Serial.println("Vb");

      Serial.print("CORRENTE DA BATERIA MPPT: ");
      x = String(canMsg.data[3]);
      Serial.print(x);
      Serial.println("Ab");

      Serial.print("Teste de potencia: ");
      n = String((canMsg.data[4])+String(canMsg.data[5]));
      Serial.println(n);


      Serial.println("-----------------------------------");
      delay(500);
    }
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;

    LAT();
    LON();
    gps.get_position(&lat, &lon, &fix_age);

    x_str = x;
    y_str = y;
    m_str = m;
    l_str = l;
    x_str.toCharArray(char_x, 3);
    y_str.toCharArray(char_y, 3);
    l_str.toCharArray(char_l, 5);
    m_str.toCharArray(char_m, 3);


    gps_str = (String(lat) + String(lon));
    gps_str.toCharArray(char_gps, 25);
    Serial.print("valor convertido: ");
    Serial.println(char_gps);

    //sprintf (lat1, "%ld", lat);
    //Serial.print("Publish message: ");

    //client.publish("Current_Input", char_x);
    //client.publish("PBattery_Voltage", char_y);
    //client.publish("Current_Output", "10");
    //client.publish("Power_Input", char_l);
    //client.publish("teste", char_m);
    client.publish("gps", char_gps);
    //client.publish("teste", "5");
  }
}



/*

 //GPS
 while (Serial.available()){
  digitalWrite (2, HIGH);
  C = Serial.read(); 
  if (gps.encode(C)){}
 }
 digitalWrite (2, LOW);
 gps.get_position(&lat, &lon, &fix_age);
 unsigned long currentMillis = millis();    //Tempo atual em ms


   //CAN
   if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id  == 36){
      
      Serial.print("CORRENTE DA BATERIA MPPT: ");
      x = String(((canMsg.data[0]))+String((canMsg.data[1])));
      Serial.print(x);
      Serial.println("Ab");


      
      Serial.print("TENSÃO DA BATERIA MPPT: ");
      y = String((canMsg.data[2])+String(canMsg.data[3])+String((canMsg.data[4])));
      Serial.print(y);
      Serial.println("Vb");
      
    }
    
    if (canMsg.can_id  == 51){
      Serial.print("POTENCIA DO PAINEL MPPT: ");
      l = String((canMsg.data[0])+String(canMsg.data[1])+String(canMsg.data[2])+String(canMsg.data[3]));
      Serial.print(l);
      Serial.println("W");
      
      Serial.print("TENSÃO PAINEL MPPT: ");
      m = String(((canMsg.data[4]))+String((canMsg.data[5])));
      Serial.print(m);
      Serial.println("Vp");
      Serial.println("-----------------------------------");
    }
   }

  //------------------------------------------------------------------------

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;
    LAT();
    LON();

    x_str = x;
    x_str.toCharArray(char_x, 3);

    y_str = y;
    y_str.toCharArray(char_y, 3);

    l_str = l;
    l_str.toCharArray(char_l, 5);

    m_str = m;
    m_str.toCharArray(char_m, 3);


    gps_str = (String(lat)+String(lon));
    gps_str.toCharArray(char_gps, 25);
    Serial.print("valor convertido: ");
    Serial.println(char_gps);

    //sprintf (lat1, "%ld", lat);
    //Serial.print("Publish message: ");

    client.publish("Current_Input", char_x);
    client.publish("PBattery_Voltage", char_y);
    client.publish("Current_Output", "10");
    client.publish("Power_Input", char_l);
    client.publish("teste", char_m);


    client.publish("gps", char_gps);
    //client.publish("teste", "5");
  }

  */