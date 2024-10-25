float sp = 0;
float heart = 0;

void setup() {
  Serial.begin(115200);
}
void loop()
{
  sp = 5 + random(5);
  heart = 100 + random(40);
  Serial.print(sp);
  Serial.print(",");
  Serial.println(heart);
  delay(1000);
}
