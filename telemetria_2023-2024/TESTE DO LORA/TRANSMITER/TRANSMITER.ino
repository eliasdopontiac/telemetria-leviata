// Transmitter code
HardwareSerial SerialAT(1);
#define KNOB 4
int readVal;

void setup() {  
  SerialAT.begin(9600,SERIAL_8N1,16,17);
}

void loop() {  
  readVal = analogRead(KNOB);
  SerialAT.println(readVal);
  delay(500);   
}
