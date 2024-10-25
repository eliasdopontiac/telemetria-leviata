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
//CONFIGURAÇÃO MILLIS
long previousMillis = 0;    // Variável de controle do tempo
long redLedInterval = 900;  // Tempo em ms do intervalo a ser executado
long lastMsg = 0;

//CONFIGURAÇÃO MPPT
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

int correntebateria2;
int potenciapainel1;
int tensaopainel1;
int tensaobateria1;
float current = 0.00;
int count = 0;

//CONFIGURAÇÃO CAN
#include <SPI.h>
#include <mcp2515.h>
#define CS 5
#include "EmonLib.h"

struct can_frame canMsg;
struct can_frame canMsg2;
struct can_frame canMsg3;

EnergyMonitor emon1;
MCP2515 mcp2515(CS);

void setup() {
  Serial.begin(115200);
  emon1.current(35, 14);

  while (!Serial);
  Serial1.begin(19200, SERIAL_8N1, 16, 17);

  mcp2515.reset();
  mcp2515.setBitrate(CAN_500KBPS, MCP_8MHZ);
  mcp2515.setNormalMode();

  Serial.println("Telemetria MPPT");
}

void loop() {

  if (Serial1.available()) {
    double Irms = emon1.calcIrms(1480);  // Calculate Irms only
    Serial.println(Irms);		       // Irms
    current = (Irms/2.6)+2.643;
    Serial.println(current);


    label = Serial1.readStringUntil('\t');           // leitura do label do MPPT
    val = Serial1.readStringUntil('\r\r\n');         // leitura do valor do label

    if (label == "I")                                // Escolha dos parametros do MPPT. Verificar no datasheet da victron para todos dos labels.
    {                                                
      val.toCharArray(buf, sizeof(buf));             // conversão do valor para array.
      float meetwaarde = atoi(buf);                  // conversão para float
      meetwaarde = meetwaarde / 1000;                // ajustando para o valor correto, por padrão virá na escala de milis.
      dtostrf(meetwaarde, len, 1, correntebateria);  // Conversão do valor calculado para string value to string
      correntebateria[len] = ' ';
      correntebateria[len + 1] = 0;
      Serial.print("Corrente da Bateria: ");
      float correntebateria1;
      correntebateria1 = atof(correntebateria);
      correntebateria2 = (correntebateria1 * 10);
      Serial.print(correntebateria2);
      Serial.println("A");
    }

    else if (label == "V")  //TENSÃO DA BATERIA
    {
      val.toCharArray(buf, sizeof(buf));
      float meetwaarde = atoi(buf);
      meetwaarde = meetwaarde / 1000;
      dtostrf(meetwaarde, len, 1, tensaobateria);
      tensaobateria[len] = ' ';
      tensaobateria[len + 1] = 0;
      Serial.print("Tensão da bateria: ");
      tensaobateria1 = atoi(tensaobateria);
      Serial.print(tensaobateria1);
      Serial.println("V");
    }

    else if (label == "VPV")  //TENSÃO DO PAINEL
    {
      val.toCharArray(buf, sizeof(buf));
      float meetwaarde = atoi(buf);
      meetwaarde = meetwaarde / 1000;
      dtostrf(meetwaarde, len, 1, tensaopainel);
      tensaopainel[len] = ' ';
      tensaopainel[len + 1] = 0;
      tensaopainel1 = atoi(tensaopainel);
      Serial.print("Tensão do painel: ");
      Serial.print(tensaopainel1);
      Serial.println("V");
    }


    else if (label == "PPV")  //POTENCIA PAINEL
    {
      val.toCharArray(buf, sizeof(buf));
      meetwaarde = atoi(buf);
      dtostrf(meetwaarde, len, 0, potenciapainel);
      potenciapainel[len] = ' ';
      potenciapainel[len + 1] = 0;
      Serial.print("Potencia do painel: ");
      potenciapainel1 = atoi(potenciapainel);
      Serial.print(potenciapainel1);
      Serial.println("W");
    }

  unsigned long now = millis();
  if (now - lastMsg > 1000) {
    lastMsg = now;
    count = count+50;
    Serial.println(count);

  }

    canMsg.can_id = 36;
    canMsg.can_dlc = 8;
    canMsg.data[0] = potenciapainel1;
    canMsg.data[1] = tensaopainel1;
    canMsg.data[2] = tensaobateria1;
    canMsg.data[3] = correntebateria2;

    if(count<100){
      //Serial.print("printando if1: ");
      //Serial.println(count);
      canMsg.data[4] = count;
    }
    
    else if(count>=100 and count<1000){
      //Serial.print("printando if2: ");
      String teste1 = String(count);  
      //Serial.println(teste1);
      String teste2 = teste1.substring(0,2);
      String teste3 = teste1.substring(2,3);
      canMsg.data[4] = (teste2.toInt());
      canMsg.data[5] = (teste3.toInt());
    }

      else if(count>=1000){
      //Serial.print("printando if2: ");
      String teste1 = String(count);
      //Serial.println(teste1);
      String teste2 = teste1.substring(0,2);
      String teste3 = teste1.substring(2,4);
      canMsg.data[4] = (teste2.toInt());
      canMsg.data[5] = (teste3.toInt());
    }
    mcp2515.sendMessage(&canMsg);
    
  }
}
