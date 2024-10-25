#include <HardwareSerial.h>

HardwareSerial SerialPort(2); // use UART2

const int rele1 = 4;
const int rele2 = 15;
const int rele3 = 2;

const int sinaleira1 = 14;
//const int sinaleira2 = 27;
const int sinaleira3 = 26;


int buttonState1 = 0;
int buttonState2 = 0;
int buttonState3 = 0;

void setup()  
{
  pinMode(rele1, INPUT);
  pinMode(rele2, INPUT);
  pinMode(rele3, INPUT);
  

  pinMode(sinaleira1, OUTPUT);
  //pinMode(sinaleira2, OUTPUT);
  pinMode(sinaleira3, OUTPUT);

  SerialPort.begin(115200, SERIAL_8N1, 16, 17); 
  Serial.begin(115200);
} 
void loop()  
{ 
  buttonState1 = digitalRead(rele1);
  //Serial.println(buttonState1);

  buttonState2 = digitalRead(rele2);
  //Serial.println(buttonState2);

  buttonState3 = digitalRead(rele3);
  //Serial.println(buttonState2);
//////////////////
if (buttonState1 == HIGH) {
     SerialPort.print(1);
     digitalWrite(sinaleira1, HIGH);
     Serial.print("1");
  } else {
    // turn LED off
    SerialPort.print(0);
    digitalWrite(sinaleira1, LOW);
    Serial.print("0");
  }
//////////////////
if (buttonState2 == HIGH) {
     SerialPort.print(3);
     Serial.print("3");
  } else {
    // turn LED off
    SerialPort.print(2);
    Serial.print("2");
  }
/////////////////
if (buttonState3 == HIGH) {
     SerialPort.print(5);
     Serial.println("5");
  } else {
    // turn LED off
    SerialPort.print(4);
    Serial.println("4");
  }
}
