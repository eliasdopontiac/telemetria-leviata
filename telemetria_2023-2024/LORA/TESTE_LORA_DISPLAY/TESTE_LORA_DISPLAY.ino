/*
LDC     ESP32       LORA
GND     GND         GND
VCC     VIN         
RS      D15
R/W     D13
E       D14
PSB     GND
RST     GPIO 22
BLA     VDD(3V3)    VCC
BLK     GND         GND
        D2          DIO0
        D12         RST
        D19         MISO
        D5          NSS
        D23         MOSI
*/
#include <LoRa.h>
#include <SPI.h>
 
#define ss 5
#define rst 12
#define dio0 2


 
#include <Arduino.h>
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

U8G2_ST7920_128X64_F_SW_SPI u8g2(U8G2_R0, /* clock=*/ 14, /* data=*/ 13, /* CS=*/ 5, /* reset=*/ 22); // ESP32


// End of constructor list

void setup() {
  
  u8g2.begin();
  
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Receiver");
 
  LoRa.setPins(ss, rst, dio0);    //setup LoRa transceiver module
 
  while (!LoRa.begin(433E6))     //433E6 - Asia, 866E6 - Europe, 915E6 - North America
  {
    Serial.println(".");
    delay(500);
  }
  LoRa.setSyncWord(0xA5);
  Serial.println("LoRa Initializing OK!");
}

void loop() {

  int packetSize = LoRa.parsePacket();    // try to parse packet
  if (packetSize) 
  {
    
    Serial.print("Received packet '");
 
    while (LoRa.available())              // read packet
    {
      String LoRaData = LoRa.readString();
      
      u8g2.clearBuffer();          // clear the internal memory
      u8g2.setFont(u8g2_font_ncenB08_tr); // choose a suitable font
      u8g2.setCursor(0,10);
      u8g2.print((LoRaData));  // write something to the internal memory
      Serial.print(LoRaData);
    }
    u8g2.setCursor(0,20);
    u8g2.print(LoRa.packetRssi());
    Serial.print("' with RSSI ");         // print RSSI of packet
    Serial.println(LoRa.packetRssi());
    u8g2.sendBuffer();          // transfer internal memory to the display
  }
  delay(10);
}
