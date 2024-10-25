String a = "0";
String b = "9";

String c;
void setup() {
  Serial.begin(9600);
 
}
void loop() {
  int x = b.toInt();
  
  if (x<10){
    c = b+a;
  }
Serial.println(c);
delay(1000);
}
