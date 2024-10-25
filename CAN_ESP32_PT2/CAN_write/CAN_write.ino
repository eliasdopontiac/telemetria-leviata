/*MCP2515     ESP32
 *INT    -     D15 
 *SCK    -     D18 
 *SI     -     D23 
 *SO     -     D19
 *GND    -     GND
 *VCC    -     3V3
*/
//17.3  -   17.3  -   173   -   17.3
//9.3   -   09.3  -   093   -   09.3

#include <SPI.h>
#include <mcp2515.h>
#define CS 2

float a = 1.0;    //Tensão
float b = 93.3;   //Corrente
float c = 6.6;    //Constante

String myStr_a;
String myStr_b;
String myStr_c;
String teste = "";

struct can_frame canMsg1;
struct can_frame canMsg2;
struct can_frame canMsg3;


MCP2515 mcp2515(CS);

void setup() {
  //Tensão
  pinMode(CS, OUTPUT);

  if (a<10.0 and a>=1.0){
   myStr_a = "0"+String(a);
  }
  else{
    myStr_a = String(a);
  }
  
  
  //Corrente

  if (b<10.0 and b>=1.0){
   myStr_b = "0"+String(b);
  }
  else{
    myStr_b = String(b);
  }
  
  //Constante
  if (c<10.0 and c>=1.0){
   myStr_c = "0"+String(c);
  }
  else{
    myStr_c = String(c);
  }

  //Mensagem de Corrente
  canMsg1.can_id  = 36;
  canMsg1.can_dlc = 6;
  canMsg1.data[0] = 'A';
  canMsg1.data[1] = 'A'; 
  //canMsg1.data[2] = atof (myStr_a.substring(2,3).c_str ());
  canMsg1.data[2] = atof (myStr_a.substring(3,4).c_str ());
  //Mensagem de Tensão
  canMsg1.data[3] = atof (myStr_b.substring(0,1).c_str ());
  canMsg1.data[4] = atof (myStr_b.substring(1,2).c_str ()); 
  //canMsg2.data[2] = atof (myStr_b.substring(2,3).c_str ());
  canMsg1.data[5] = atof (myStr_b.substring(3,4).c_str ());
  //////////////////////
  
  //Constante
  canMsg2.can_id  = 51;
  canMsg2.can_dlc = 6;
  canMsg2.data[0] = atof (myStr_c.substring(0,1).c_str ());
  canMsg2.data[1] = atof (myStr_c.substring(1,2).c_str ()); 
  //canMsg1.data[2] = atof (myStr_a.substring(2,3).c_str ());
  canMsg2.data[2] = atof (myStr_c.substring(3,4).c_str ());



  canMsg3.can_id  = 12;
  canMsg3.can_dlc = 0;
  canMsg3.data[0] = 'A';
  
  
  while (!Serial);
  Serial.begin(19200);
  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("Example: Write to CAN");
}

void loop() {
digitalWrite(CS, LOW);

mcp2515.sendMessage(&canMsg1);
Serial.println("Mensagem 1 enviada");
delay(100);
mcp2515.sendMessage(&canMsg2);     
Serial.println("Mensagem 2 enviada");   
delay(100);

}
