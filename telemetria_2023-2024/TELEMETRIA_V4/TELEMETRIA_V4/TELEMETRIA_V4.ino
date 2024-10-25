/*
MULTIPLEX  |  ESP32
SIG        |  D39
S0         |  D15
EN         |  GND
VCC        |  Vin
GND        |  GND
C1         |  SinalPot

PWM        |  D33

LCD(2004)  |  ESP32
VCC        |  5V
GND        |  GND
SDA        |  D26
SCL        |  D25

GPS VK2828 |  ESP32
VCC        |  3V3
GND        |  GND
RX         |  D34
TX         |  D22

BMV        |  ESP32
GND        |  GND
RX         |  D36

LCD GRANDE |  ESP32
GND        |  GND
VCC        |  5V
RS         |  D13
R/W        |  D27
E          |  D14
PSB        |  GND
RST        |  D2
BLA        |  3V3
GND        |  GND

MCP2515    |  ESP32
SCK        |  D18 
SI         |  D23 
SO         |  D19
GND        |  GND
VCC        |  3V3

SD CARD    |  ESP32
MISO       |  D19
VSS2       |  GND
SCK        |  D18
VDD        |  3V3
VSS1       |  GND
MOSI       |  D23
SS         |  D5

Amp LM386  |  ESP32
VCC        |  VIN
IN         |  D4
GND        |  GND
*/

//BIBLIOTECAS AFINS
#include <Wire.h>
#include <Arduino.h>
#include <U8g2lib.h>
#include <LiquidCrystal_I2C.h>
#include <SPI.h>
#include <mcp2515.h>
#include "VeDirectFrameHandler.h"
#include <TinyGPS.h>
TinyGPS gps;
VeDirectFrameHandler myve; 
LiquidCrystal_I2C lcd(0x27,20,4);

//DEFINIÇÕES DE PORTA LADO ESQUERDO
//#define RS 13
//#define RST 12
//#define E 14
//#define RW 27
#define I2C_SDA 26 //SDA LCD
#define I2C_SCL 25 //SCL  LCD
#define pinPWM 33
#define TX_SIM800 32
#define RX_SIM800 35
#define RX_GPS 34  // RX GPS
#define analog 2  // Potenciometro
#define RX_BMV 36  // RX BMV


//DEFINIÇÕES DE PORTA LADO DIREITO
#define S0     15  // S0 multiplex
#define CS 21 // Chip Select CAN



//PINOS NÃO USADOS
#define TX_GPS 22 // TX GPS
#define TX_BMV 12 // TX BMV



//DEFINIÇÕES EXTRAS
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
U8G2_ST7920_128X64_F_SW_SPI u8g2(U8G2_R0, 18, 23, 13, U8G2_PIN_NONE); // (E, RW, RS, RST)

const int frequenciaPWM = 4200; // Frecuencia del PWM en Hz
const int resolucaoPWM = 8; // Resolución del PWM (0-255)
String data = "";
long lat;
long lon;
unsigned myAnalogRead(short inputCH, short an_in);  //função para leitura do MUX 16
unsigned long fix_age;
struct can_frame canMsg;
int analogVal1;
int DEG;
int MIN1;
int MIN2;
int c;

MCP2515 mcp2515(CS);
String x;
String y;
float a = 0.0;
float b = 0.0;


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
  
  Serial.print("Latitude");
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

  Serial.print("Longitude");
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
      
    }
    if(String(myve.veName[i]) == "I") {

        Serial.print(myve.veName[i]);
        Serial.print("= ");
        Serial.println(atof(myve.veValue[i]));
        
      }
    if(String(myve.veName[i]) == "P") {

        Serial.print(myve.veName[i]);
        Serial.print("= ");
        Serial.println(atof(myve.veValue[i]));
        
      }
  }
  lcd.clear();
}

unsigned myAnalogRead(short inputCH, short an_in)
{
  unsigned analogVal;
  digitalWrite(S0, HIGH);         
  analogVal = analogRead(an_in);
  return analogVal;
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

void PWM(){
  
  static unsigned long prev_millis;
  
    analogVal1 = map(myAnalogRead(1,analog), 0, 4095, 0 , 180);
    Serial.println(analogVal1);
    ledcWrite(0, analogVal1);
  
}

/*void CAN_READ(){
  if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    if (canMsg.can_id  == 36){    
      Serial.print("primeiro: ");
      //Serial.print(canMsg.data[0]);

      x = String((canMsg.data[0]))+String((canMsg.data[1]))+String((canMsg.data[2]));
      a = x.toFloat();
      Serial.println(a/10);

      y = String((canMsg.data[3]))+String((canMsg.data[4]))+String((canMsg.data[5]));
      b = y.toFloat();
      Serial.println(b/10);
    }
  }
}

*/
void LCD_PEQUENO(){
  LAT();
  LON();
  lcd.setCursor(0, 2);
  lcd.print("POT:");
  lcd.print(analogVal1);
}

void LCD_GRANDE(){
  u8g2.clearBuffer();          // clear the internal memory
  u8g2.setFont(u8g2_font_ncenB08_tr); // choose a suitable font
  u8g2.drawStr(0,10,"Hello World!");  // write something to the internal memory
  u8g2.sendBuffer();          // transfer internal memory to the display
  //delay(1000);
}

void setup() 
{
  Serial.begin(115200);  
  Serial1.begin(9600, SERIAL_8N1, RX_GPS, TX_GPS); //Mudança de pino GPS
  Serial2.begin(19200, SERIAL_8N1, RX_BMV, TX_BMV); //Mudança de pino BMV
  Wire.begin(I2C_SDA, I2C_SCL); //Mudança de pino LCD
  
  pinMode(RX_GPS, INPUT);
  pinMode(TX_GPS, OUTPUT);
  pinMode(S0, OUTPUT);
  pinMode(pinPWM, OUTPUT);
  digitalWrite(S0,  LOW);  

  ledcSetup(0, frequenciaPWM, resolucaoPWM);
  ledcAttachPin(pinPWM, 0);

  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("------- CAN Read ----------");


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
  ReadVEData();
  EverySecond();
  GPS();
  PWM();
  //CAN_READ();
  LCD_PEQUENO();
  LCD_GRANDE();
}
