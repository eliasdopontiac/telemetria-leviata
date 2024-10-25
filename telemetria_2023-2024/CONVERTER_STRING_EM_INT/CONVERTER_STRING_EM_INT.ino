int a = 10;
String myStr;


void setup() {
  Serial.begin(9600);
 
}
void loop() {
  myStr = String(a);
  String sub = myStr.substring(0, 1);
  Serial.println(sub);
  delay(1000);
}
