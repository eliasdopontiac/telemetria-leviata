// Receiver code
HardwareSerial SerialAT(1);

void setup() {  
  Serial.begin(9600);
  SerialAT.begin(9600,SERIAL_8N1,16,17);
}

void loop() {  
  if (SerialAT.available()) {
    Serial.write(SerialAT.read());
  }  
}
