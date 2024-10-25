/* CONEXÕES:
     MPPT        Arduino pin
     GND         GND
     RX          -
     TX          RX2
     Power       -
 */

byte len = 5;
int intmeetwaarde;
String label, val;

float meetwaarde;
char buf[45];
//char voorloop[12];
//char laadstatus[12];
//char foutmelding[12];

char correntebateria[6];
char potenciapainel[6];
char rendimentoontem[6];
char potenciamaximaontem[6];
char rendimentohoje[6];
char tensaopainel[6];
char tensaobateria[6];
char correntepainel[12];

void setup()  
{

  Serial.begin(19200);
  Serial1.begin(19200, SERIAL_8N1, 16, 17);                   // Iniciando comunicação do Mppt com o ESP32 através da porta Serial 1
} 

void loop() 
{
  if (Serial1.available())
   {
        loop_mppt();
   }
}
