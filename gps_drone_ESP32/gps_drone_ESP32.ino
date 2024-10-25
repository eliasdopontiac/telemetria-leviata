// GPS(PIN)  -    ESP32(PIN)      //    LCD     -     ESP32(PIN)
// V         -    3V3             //    GND     -     GND
// T         -    RX0             //    VCC     -     5V
// R         -    TX0             //    SDA     -     GPIO 21
// G         -    GND             //    SCL     -     GPIO 22
//


#include <TinyGPS.h>


TinyGPS gps;
long lat;
long lon;
unsigned long fix_age;
int DEG;
int MIN1;
int MIN2;
int c;
//
//************* routine di esposizione della latitudine (in gradi decimali) *************
//
void LAT()
{
  Serial.println(lat);
  /*
 DEG = lat / 1000000;
 MIN1 = (lat / 10000) % 100;
 MIN2 = lat % 10000;
 //lcd.setCursor (0,0);
 Serial.print("LAT:");
 Serial.print(DEG);
 //Serial.write(0xDF);
 Serial.print(MIN1);
 Serial.print(".");
 Serial.print(MIN2);
 Serial.print("' ");
 */
}
//
// ************ routine di esposizione della longitudine (in gradi decimali) ***********
//
void LON()
{
 Serial.println(lon);
 /*
 DEG = lon / 1000000;
 MIN1 = (lon / 10000) % 100;
 MIN2 = lon % 10000;
 //lcd.setCursor(0, 1);
 Serial.print("LON:");
 Serial.print(DEG);
 
 //lcd.write(0xDF);
 Serial.print(MIN1);

 Serial.print(".");
 Serial.print(MIN2);
 
 lcd.print("' ");
 */
}
//
//
void setup()
{
 Serial.begin(9600); // definisce la velocita' (il baudrate) dei dati dal ricevitore GPS
 /*lcd.init(); // inizializza il display
lcd.backlight();
*/
 delay(3000); //attende tre secondi per consentire la lettura del display
}
//
//
void loop()
{
 while (Serial.available())
 {
 digitalWrite (13, HIGH);
 c = Serial.read(); // legge i dati provenienti dal modulo GPS
 if (gps.encode(c)) // apparentemente inutile, forse decodifica i dati provenienti dal GPS
 {
 // inserire qui una eventuale codifica di trattamento del segnale ricevuto
 }
 }
 digitalWrite (13, LOW);
 gps.get_position(&lat, &lon, &fix_age); // lat/long (segnati) in millesimi di grado decimale
 LAT(); // lancia la routine di esposizione della latitudine
 LON(); // lancia la routine di esposizione della longitudine
}
