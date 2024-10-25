// DISPLAY -> ARDUINO MEGA
//GND      -> GND
//VCC      -> 5V
//SDA      -> SDA 20
//SCL      -> SCL 21
//
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
//Inicializa o display no endereco 0x27
LiquidCrystal_I2C lcd(0x27,20,4);
 
void setup()
{
 lcd.init();
}
 
void loop()
{
  lcd.setBacklight(HIGH);
  lcd.setCursor(0,0);
  lcd.print("KIBE SEM ORELHA");
  lcd.setCursor(0,1);
  lcd.print("KIBE SURDO");
  lcd.setCursor(0,2);
  lcd.print("");
  
  delay(10000);
  
}
