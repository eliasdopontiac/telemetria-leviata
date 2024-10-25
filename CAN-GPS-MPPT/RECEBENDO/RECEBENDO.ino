/*MCP2515     ESP32
 *INT         D15 
 *SCK         D18 
 *SI          D23 
 *SO          D19
 *CS          D5
 *GND         GND
 *VCC         3V3

 *GPS(PIN)  -    ESP32(PIN)      //    LCD     -     ESP32(PIN)
 *V         -    3V3             //    GND     -     GND
 *T         -    RX0             //    VCC     -     5V
 *R         -    TX0             //    SDA     -     GPIO 21
 *G         -    GND             //    SCL     -     GPIO 22
*/
#include <SPI.h>
#include <mcp2515.h>
#define CS 5

struct can_frame canMsg;


MCP2515 mcp2515(CS);

String x;
String y;
String l;
String m;

float a = 0.0;
float b = 0.0;
float c = 0.0;
float d = 0.0;

void setup() {
  Serial.begin(9600);
  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("------- CAN Read ----------");
}

void loop() {


   if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    //Serial.print(canMsg.can_id); // print ID
    if (canMsg.can_id  == 36){
      
     
      Serial.print("primeiro: ");
      /*Serial.print(canMsg.data[0]);
      Serial.print(canMsg.data[1]);
      Serial.print(canMsg.data[2]);
      Serial.print(canMsg.data[3]);
      Serial.print(canMsg.data[4]);
      Serial.println(canMsg.data[5]);
      */
      x = String((canMsg.data[0]))+String((canMsg.data[1]))+String((canMsg.data[2]));
      a = x.toFloat();
      Serial.println(a/10);

      y = String((canMsg.data[3]))+String((canMsg.data[4]))+String((canMsg.data[5]));
      b = y.toFloat();
      Serial.println(b/10);

    }
    if (canMsg.can_id  == 51){
      
      Serial.print("Segundo: ");
      /*Serial.print(canMsg.data[0]);
      Serial.print(canMsg.data[1]);
      Serial.print(canMsg.data[2]);
      Serial.print(canMsg.data[3]);
      Serial.print(canMsg.data[4]);
      Serial.println(canMsg.data[5]);
*/
      l = String((canMsg.data[0]))+String((canMsg.data[1]))+String((canMsg.data[2]));
      c = l.toFloat();
      Serial.println(c/10);
/*
      y = String((canMsg.data[3]))+String((canMsg.data[4]))+String((canMsg.data[5]));
      b = y.toFloat();
      Serial.println(b/10);
      */
    }

    
    /*for (int i = 0; i<canMsg.can_dlc; i++)  {  // print the data
      Serial.print(canMsg.data[i]);
  }*/
  }
  
   
  Serial.println(" ");
  
  delay(100);
  }
