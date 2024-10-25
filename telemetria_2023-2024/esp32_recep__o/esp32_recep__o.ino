#include <Wire.h>

#include <LiquidCrystal_I2C.h>

#include <mcp_can.h>
#include <mcp_can_dfs.h>
#include <SPI.h>

long unsigned int rxId;
unsigned char len = 0;
unsigned char rxBuf[7];
char msgString[128];
float dados[6];
int dadosInt[2];
char msg[7];
LiquidCrystal_I2C lcd(0x27, 20, 4);

int contador = 0;

#define CAN0_INT 2
MCP_CAN CAN0(5); //cs pin 5

void setup() {
  Serial.begin(115200);

  lcd.init();
  lcd.backlight();
  lcd.print("Hello World");
 
  if (CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_16MHZ) == CAN_OK){ 
  
  Serial.println("MCP2515 Initialized Successfully!"); //iniciando
  
  }
  else Serial.println("Error Initializing MCP2515...");
  
  CAN0.setMode(MCP_NORMAL);
  pinMode(CAN0_INT, INPUT);                            // Configuring pin for /INT input
  Serial.println("MCP2515 Library Receive Example...");
}

void loop(){

  if (!digitalRead(CAN0_INT))                        // se can0_int for 0, ele le o buffer recebido
  {
    CAN0.readMsgBuf(&rxId, &len, rxBuf);      // lendo dado: len = tamanho do dado, buf = dado byte(s)
    Serial.print(len);
    for (byte i = 0; i < len; i++) {
        /*if (contador <= 5) {
          contador++;
          dados[contador] = rxBuf[i];
          Serial.print(rxBuf[i]);
        } else {
          contador++;
          dadosInt[i] = rxBuf[i];
          if (contador > 7) {
            contador = 0;
          }*/
          Serial.print("Mensagem recebida com sucesso: ");
          Serial.println((char)rxBuf[i]);
        }
      }
  /*for (int i = 0; i++; i < 6) {
    Serial.print(dadosInt[i]);
    Serial.print(" ");
  }*/
  String palavra = "";
  for (int i; i < len; i++){
    palavra += (char)rxBuf[i];
  }
  Serial.print(palavra);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(palavra);
  delay(500);

  
}
