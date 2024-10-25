/*
LCD(2004)  |  ESP32
VCC        |  5V
GND        |  GND
SDA        |  D26
SCL        |  D25

GPS VK2828 |  ESP32
VCC        |  3V3
GND        |  GND
RX         |  D32
TX         |  D35

BMV        |  ESP32
GND        |  GND
RX         |  D34

LCD GRANDE |  ESP32
GND        |  GND
VCC        |  5V
RS         |  D5
R/W        |  D12
E          |  D14
RST        |  D22
BLA        |  3V3
BLK        |  GND

MCP2515    |  ESP32
SCK        |  D18
SI         |  D23
SO         |  D19
GND        |  GND
CS         |  D21
VCC        |  3V3

SD CARD    |  ESP32
MISO       |  D
VSS2       |  GND
SCK        |  D
VDD        |  3V3
VSS1       |  GND
MOSI       |  D
SS         |  D

Amp LM386  |  ESP32
VCC        |  VIN
IN         |  D
GND        |  GND
*/

//BIBLIOTECAS AFINS
#include <Wire.h>
#include <Arduino.h>
#include <U8g2lib.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <esp_now.h>
#include <WiFi.h>
#include <mcp2515.h>
#include "VeDirectFrameHandler.h"
#include <TinyGPS.h>

#include <HardwareSerial.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

TinyGPS gps;
VeDirectFrameHandler myve; 
LiquidCrystal_I2C lcd(0x27,20,4);
char number  = ' ';
int LED = 2;

//DEFINIÇÕES DE PORTA
#define RS 5 //LCDZAO
#define E 14 //LCDZAO
#define RW 12 //LCDZAO
#define RST 22 //LCDZAO

#define I2C_SDA 26 //SDA LCD
#define I2C_SCL 25 //SCL  LCD

//#define TX_SIM800 NULL
//#define RX_SIM800 NULL

#define RX_GPS 35  // RX GPS
#define TX_GPS NULL // TX GPS

#define RX_BMV 34  // RX BMV

#define CS 2 // Chip Select CAN

// Define os pinos para RX e TX
#define RX_PIN_3 15
#define TX_PIN_3 21

U8G2_ST7920_128X64_F_SW_SPI u8g2(U8G2_R0, 14, 12, 5, 22);
//U8G2_ST7920_128X64_F_SW_SPI u8g2(U8G2_R0, E, RW, RS, RST);

String data = "";
long lat;
long lon;
unsigned long fix_age;
struct can_frame canMsg;
int DEG;
int MIN1;
int MIN2;
int c;

MCP2515 mcp2515(CS);
String x;
String y;
float a = 0.0;
float b = 0.0;

String Potin;
String Vin;
String Iin;

//variaveis BMV
String P;
String V;
String I;

typedef struct struct_message {
    float V_B;
    float C_B;
    float V_P;
    float P_P;
} 
struct_message;
struct_message myData;

void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&myData, incomingData, sizeof(myData));

  Serial.print("Tensao Bateria: ");
  Serial.println(myData.V_B);
  Serial.print("Corrente Bateria: ");
  Serial.println(myData.C_B);
  Serial.print("Tensao Painel: ");
  Serial.println(myData.V_P);
  Serial.print("Potencia Painel: ");
  Serial.println(myData.P_P);
  Serial.println();

  Potin = float(myData.P_P);
  Vin = float(myData.V_P);
  Iin = float(myData.C_B);
}

void LAT()
{
  DEG = lat / 1000000;
  MIN1 = (lat / 10000) % 100;
  MIN2 = lat % 10000;
  lcd.setCursor (0,0);
  lcd.print("LAT:");
  lcd.print(DEG);
  lcd.write(0xDF);
  lcd.print(MIN1);
  lcd.print(".");
  lcd.print(MIN2);
  lcd.print("' ");
  
  Serial.print("Latitude: ");
  Serial.println(lat);

}

void LON()
{
  DEG = lon / 1000000;
  MIN1 = (lon / 10000) % 100;
  MIN2 = lon % 10000;
  lcd.setCursor(0, 1);
  lcd.print("LON:");
  lcd.print(DEG);
  lcd.write(0xDF);
  lcd.print(MIN1);
  lcd.print(".");
  lcd.print(MIN2);
  lcd.print("' ");

  Serial.print("Longitude: ");
  Serial.println(lon);
}

void HexCallback(const char* buffer, int size, void* data) {
  char tmp[100];
  memcpy(tmp, buffer, size * sizeof(char));
  tmp[size] = 0;
  Serial.print("received hex frame: ");
  Serial.println(tmp);
}

// log helper
void LogHelper(const char* module, const char* error) {
  Serial.print(module);
  Serial.print(":");
  Serial.println(error);
}


void ReadVEData() {
  while (Serial2.available()) {
    myve.rxData(Serial2.read());
  }
}

void EverySecond() {
  static unsigned long prev_millis;

  if (millis() - prev_millis > 1000) {
    PrintData();
    prev_millis = millis();
  }
}

void PrintData() {
  for (int i = 0; i <=18; i++) {
    if (String(myve.veName[i]) == "V") {
      
      Serial.print(myve.veName[i]);
      Serial.print("= ");
      Serial.println(atof(myve.veValue[i]) / 1000);
      V = (atof(myve.veValue[i]) / 1000);
      
    }
    if(String(myve.veName[i]) == "I") {

        Serial.print(myve.veName[i]);
        Serial.print("= ");
        Serial.println(atof(myve.veValue[i]) / 1000);
        I = (atof(myve.veValue[i]) / 1000);
        
      }
    if(String(myve.veName[i]) == "P") {

        Serial.print(myve.veName[i]);
        Serial.print("= ");
        Serial.println(atof(myve.veValue[i]));
        P = (atof(myve.veValue[i]) / 1000);
        
      }
  }
  lcd.clear();
}


void GPS(){
  while (Serial1.available())
  {    
    c = Serial1.read();
    if (gps.encode(c))
    {
      // Tratamento dos dados do GPS, se necessário
    }
  }
  gps.get_position(&lat, &lon, &fix_age);   
}

void ESP_NOW(){

  }


void LCD_PEQUENO(){
  LAT();
  LON();
  lcd.setCursor(0, 2);
}

void LCD_GRANDE(){
  u8g2.clearBuffer();          // clear the internal memory
  u8g2.setFont(u8g2_font_synchronizer_nbp_tf); // choose a suitable font
  u8g2.drawStr(0,8,"Vout: ");
  u8g2.drawStr(0,16,"Iout: ");
  u8g2.drawStr(0,24,"Pout: ");
  u8g2.drawStr(0,32,"Vin: ");
  u8g2.drawStr(0,40,"Iin: ");
  u8g2.drawStr(0,48,"Pin: ");

  // Convertendo as variáveis para const char* antes de passá-las para drawStr
  const char* V_char = V.c_str();
  const char* I_char = I.c_str();
  const char* P_char = P.c_str();

  const char* V1_char = Vin.c_str();
  const char* I1_char = Iin.c_str();
  const char* P1_char = Potin.c_str();
  
  // Desenhando as strings convertidas
  u8g2.drawStr(60,8, V_char);
  u8g2.drawStr(60,16, I_char);
  u8g2.drawStr(60,24, P_char);

  u8g2.drawStr(60,32, V1_char);
  u8g2.drawStr(60,40, I1_char);
  u8g2.drawStr(60,48, P1_char);

  
  u8g2.sendBuffer();          // transfer internal memory to the display

}

void setup() 
{
  Serial.begin(115200);  
  WiFi.mode(WIFI_STA);
  Serial1.begin(9600, SERIAL_8N1, RX_GPS, TX_GPS); //Mudança de pino GPS
  Serial2.begin(19200, SERIAL_8N1, RX_BMV, NULL); //Mudança de pino BMV
  Wire.begin(I2C_SDA, I2C_SCL); //Mudança de pino LCD
  pinMode(LED, OUTPUT);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(OnDataRecv);

  u8g2.begin();
  
  lcd.init();
  lcd.setBacklight(HIGH);
  lcd.setCursor(0,0);
  lcd.print("SEJAM BEM VINDOS");
  lcd.setCursor(0,1);
  lcd.print("AO PROJETO");
  lcd.setCursor(0,2);
  lcd.print("LEVIATA");
  lcd.setCursor(0,3);
  lcd.print("TELEMETRIA 2.0");
  delay(1500);
  lcd.clear();
} 

void loop() 
{
  LCD_GRANDE();
  ReadVEData();
  EverySecond();
  GPS();
  LCD_PEQUENO();
  ESP_NOW();
}
