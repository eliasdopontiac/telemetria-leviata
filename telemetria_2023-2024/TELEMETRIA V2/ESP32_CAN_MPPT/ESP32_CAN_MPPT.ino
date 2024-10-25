/*MCP2515     ESP32
 *INT    -     D15 
 *SCK    -     D18 
 *SI     -     D23 
 *SO     -     D19
 *GND    -     GND
 *VCC    -     3V3
CONEXÕES COM MPPT:
  MPPT   -     Arduino pin
  GND    -     GND
  RX     -     -
  TX     -     RX2
  Power        -
*/
////////////////////////////////////////////////////////////////////
//CONFIGURAÇÃO MILLIS

long previousMillis = 0;        // Variável de controle do tempo
long redLedInterval = 900;     // Tempo em ms do intervalo a ser executado

////////////////////////////////////////////////////////////////////
//CONFIGURAÇÃO MPPT
////////////////////////////////////////////////////////////////////
byte len = 5;
int intmeetwaarde;
String label, val;

float meetwaarde;
char buf[45];

char correntebateria[6];
char potenciapainel[6];
char rendimentoontem[6];
char potenciamaximaontem[6];
char rendimentohoje[6];
char tensaopainel[6];
char tensaobateria[6];
char correntepainel[12];

String correntebateria1;
String potenciapainel1;
String tensaopainel1;
String tensaobateria1;
///////////////////////////////////////////////////////////////////////
//CONFIGURAÇÃO CAN
///////////////////////////////////////////////////////////////////////
#include <SPI.h>
#include <mcp2515.h>
#define CS 5

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

  canMsg3.can_id  = 12;
  canMsg3.can_dlc = 0;
  canMsg3.data[0] = 'A';
  
  
  while (!Serial);
  Serial.begin(115200);
  Serial1.begin(19200, SERIAL_8N1, 16, 17);
  
  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();
  
  Serial.println("Example: Write to CAN");
}

void loop() {

if (Serial1.available())
   {
  
        label = Serial1.readStringUntil('\t');                // this is the actual line that reads the label from the MPPT controller
        val = Serial1.readStringUntil('\r\r\n');              // this is the line that reads the value of the label



     if (label == "I")                                        // I chose to select certain paramaters that were good for me. check the Victron whitepaper for all labels.
     {                                                        // In this case I chose to read charging current
        val.toCharArray(buf, sizeof(buf));                    // conversion of val to a character array. Don't ask me why, I saw it in one of the examples of Adafruit and it works.
        float meetwaarde = atoi(buf);                         // conversion to float
        meetwaarde = meetwaarde/1000;                         // calculating the correct value, see the Victron whitepaper for details. The value of label I is communicated in milli amps.
        dtostrf(meetwaarde, len, 0, correntebateria);              // conversion of calculated value to string
        correntebateria[len] = ' '; correntebateria[len+1] = 0;
        Serial.print("Corrente da Bateria: ");
        if (atoi(correntebateria)<10){
            correntebateria1 = "0"+String(atoi(correntebateria));
            }
        if (atoi(correntebateria)<10){
            correntebateria1 = String(atoi(correntebateria));
        }
        Serial.print((correntebateria1));
        Serial.println("A");
     }
     
     else if (label == "V")        //TENSÃO DA BATERIA                    
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atoi(buf);
        meetwaarde=meetwaarde/1000;
        dtostrf(meetwaarde, len, 0, tensaobateria);
        tensaobateria[len] = ' '; tensaobateria[len+1] = 0;
        Serial.print("Tensão da bateria: "); 
        Serial.print(atoi(tensaobateria));
        Serial.println("V");
     }

     else if (label == "VPV")        //TENSÃO DO PAINEL                    
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atoi(buf);
        meetwaarde=meetwaarde/1000;
        dtostrf(meetwaarde, len, 0, tensaopainel);
        tensaopainel[len] = ' '; tensaopainel[len+1] = 0; 
        Serial.print("Tensão do painel: "); 
        Serial.print(atoi(tensaopainel));
        Serial.println("V");
     }

         
     else if (label == "PPV")      //POTENCIA PAINEL                 
     {
        val.toCharArray(buf, sizeof(buf));                    
        meetwaarde = atoi(buf);                               
        dtostrf(meetwaarde, len, 0, potenciapainel);          
        potenciapainel[len] = ' '; potenciapainel[len+1] = 0; 
        Serial.print("Potencia do painel: "); 
        if (atoi(potenciapainel)>1000){
          potenciapainel1  = String(atoi(potenciapainel));
        }
        if (atoi(potenciapainel)>=100 and atoi(potenciapainel)<1000){
          potenciapainel1 = "0"+String(atoi(potenciapainel));
          }
        if (atoi(potenciapainel)<10){
          potenciapainel1 = "000"+String(atoi(potenciapainel));
          }
                
        Serial.print(potenciapainel1);
        Serial.println("W");
          }
     }

  tensaopainel1    = String(atoi(tensaopainel));
  tensaobateria1   = String(atoi(tensaobateria));


  canMsg1.can_id  = 36;
  canMsg1.can_dlc = 6;
  canMsg1.data[0] = atoi (correntebateria1.substring(0,1).c_str ());
  canMsg1.data[1] = atoi (correntebateria1.substring(1,2).c_str ()); 
  
  //Mensagem de Tensão
  canMsg1.data[2] = atoi (tensaobateria1.substring(0,1).c_str ());
  canMsg1.data[3] = atoi (tensaobateria1.substring(1,2).c_str ());
  canMsg1.data[4] = atoi (tensaobateria1.substring(3,4).c_str ());   


  canMsg2.can_id  = 51;
  canMsg2.can_dlc = 6;
  canMsg2.data[0] = atoi (potenciapainel1.substring(0,1).c_str ());
  canMsg2.data[1] = atoi (potenciapainel1.substring(1,2).c_str ()); 
  canMsg2.data[2] = atoi (potenciapainel1.substring(2,3).c_str ());
  canMsg2.data[3] = atoi (potenciapainel1.substring(3,4).c_str ());
  
  canMsg2.data[4] = atoi (tensaopainel1.substring(0,1).c_str ());
  canMsg2.data[5] = atoi (tensaopainel1.substring(1,2).c_str ()); 
 
  
    mcp2515.sendMessage(&canMsg1);
    mcp2515.sendMessage(&canMsg2);     
 //Serial.println(correntebateria1);
 //Serial.println(tensaobateria1);
  
   }
