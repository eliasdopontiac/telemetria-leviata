char potenciapainel;
void setup()
{
Serial.begin(19200);
}

void loop() {   
if (Serial.available() > 0) 
{
  String data = Serial.readStringUntil('\n');
  Serial.println(data);
  //Serial.println(potenciapainel);
}
}
