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
 
void setup() 
{
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
 
void loop() 
{
  int packetSize = LoRa.parsePacket();    // try to parse packet
  if (packetSize) 
  {
    
    Serial.print("Received packet '");
 
    while (LoRa.available())              // read packet
    {
      String LoRaData = LoRa.readString();
      Serial.print(LoRaData); 
    }
    Serial.print("' with RSSI ");         // print RSSI of packet
    Serial.println(LoRa.packetRssi());
  }
}
