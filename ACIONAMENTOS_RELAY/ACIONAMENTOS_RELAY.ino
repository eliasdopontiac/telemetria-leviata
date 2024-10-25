/*CÓDIGO PARA ACIONAMENTOS
 * A tecnologia de acionamentos será manual e automática.
 * 
 * Como os nossos floats swiths não são precisos, foi criada a idéia de usar ESP-32 com sensores de 
 * nível de água para fazer esse controle preciso de água no casco e quando o sensor sentir agua, 
 * ele ativa o rele e liga a bomba, e permanece ligado por 5 segundos, logo depois desliga a bomba.
 * 
 * Resumindo, essa porra vai ficar foda, boto fé.
 * PS: vai ter que ter display, vc que lute sz.
 */
 

const int analogInPin1 = 34;     //Bota na D34
const int analogInPin2 = 35;    //Bota na D35

int rele1 = 4;                   //Bota na D4
int rele2 = 5;                  //Bota na D5
int rele3 = 26;                  //Bota na D5


int valorSensor1 = 0; 
int valorSensor2 = 0;
int valorSensor3 = 0;
int valorSaida1 = 0;
int valorSaida2 = 0;
int valorSaida3 = 0;
////////
#include <HardwareSerial.h>

HardwareSerial SerialPort(2); // use UART2


char number  = ' ';
int LED = 15;




void setup() {
  //Serial.begin(9600);
  SerialPort.begin(115200, SERIAL_8N1, 16, 17);
  pinMode(rele1, OUTPUT);
  pinMode(rele2, OUTPUT);
  pinMode(rele3, OUTPUT);
}

void loop() {
  valorSensor1 = analogRead(analogInPin1); // ler a porta e armazenar a variavel
  valorSensor2 = analogRead(analogInPin2);

  
  valorSaida1 = map(valorSensor1, 0, 1023, 0, 100); // ele pega a função de 0 a 1023 e converte para porcentagem
  valorSaida2 = map(valorSensor2, 0, 1023, 0, 100);
  
  if (valorSaida1 >= 30){
   digitalWrite(rele1,1);
   //delay(10);
   //digitalWrite(rele,0);
   //*delay(10);
  }
  else{
    digitalWrite(rele1,0);
  }

  if (valorSaida2 >= 30){
   digitalWrite(rele2,1); // rele do lado do piloto
   //delay(10);
   //digitalWrite(rele2,0); // rele do lado do piloto
   //delay(10);
  }
  else{
    digitalWrite(rele2,0);
  }
//////////////////////////////////////

if (SerialPort.available())
  {
    char number = SerialPort.read();
    if (number == '0') {
      digitalWrite(rele1, LOW);
    }
    if (number == '1') {
      digitalWrite(rele1, HIGH);
    }
    ///////////////////
    if (number == '2') {
      digitalWrite(rele2, LOW);
    }
    if (number == '3') {
      digitalWrite(rele2, HIGH);
    }
    /////////////////
    if (number == '4') {
      digitalWrite(rele3, LOW);
    }
    if (number == '5') {
      digitalWrite(rele3, HIGH);
    }
  }
///////////////////////////////////////

 // monitor serial
/*
  Serial.print("sensor= ");
  Serial.print(valorSensor);
  Serial.print("\t porcentagem = ");
  Serial.println(valorSaida);
  Serial.print("sensor2= ");
  Serial.print(valorSensor2);
  Serial.print("\t porcentagem2 = ");
  Serial.println(valorSaida2);
   */
  }
