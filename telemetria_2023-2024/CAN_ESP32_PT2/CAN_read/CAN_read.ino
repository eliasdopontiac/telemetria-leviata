/*MCP2515     ESP32
 *INT         D15 
 *SCK         D18 
 *SI          D23 
 *SO          D19
 *GND         GND
 *VCC         3V3
*/
#include <SPI.h>
#include <mcp2515.h>
#define CS 2

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
  Serial.begin(115200);
  pinMode(CS, OUTPUT);
  
  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("------- CAN Read ----------");
}

void loop() {

    digitalWrite(CS, LOW);
   if (mcp2515.readMessage(&canMsg) == MCP2515::ERROR_OK) {
    //Serial.print(canMsg.can_id); // print ID
    if (canMsg.can_id  == 36){
      
     
      Serial.print("primeiro: ");
      Serial.print(canMsg.data[0]);
      Serial.print(canMsg.data[1]);
      Serial.print(canMsg.data[2]);
      Serial.print(canMsg.data[3]);
      Serial.print(canMsg.data[4]);
      Serial.println(canMsg.data[5]);
      
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
