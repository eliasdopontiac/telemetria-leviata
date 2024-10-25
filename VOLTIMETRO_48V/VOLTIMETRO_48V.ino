/*
Voltímetro DC
Um Arduino DVM baseado no conceito de divisor de tensão
*/

byte i = 0;                                  //  Variável para usar no for
float accuml = 0.00;            //  Variável para guardar o valor acumulado da temperatura
//long vin = 0.00;                    //  Variável para guardar o valor lido da temperatura

int analogInput = 0;
float vout = 0.00;
float vin = 0.00;
float R1 = 100000.0; // resistência de R1 (100K) 
float R2 = 10000.0; // resistência de R2 (10K)
int value = 0;
void setup(){
   pinMode(analogInput, INPUT);
   Serial.begin(9600);
   
}
void loop(){
   // leia o valor na entrada analógica
   value = analogRead(analogInput);
   vout = (value * 4.71) / 1024.0; // see text
   vin = vout / (R2/(R1+R2)); 
   if (vin<0.3) {
      vin=0.0;// declaração para anular a leitura indesejada!
   }

for ( i = 0; i<10; i++)
     {
           vin = vout / (R2/(R1+R2)) ;
           //Serial.println(vin);
           accuml = accuml + vin; 
           delay(10);
      }
     vin = accuml / 10;
     Serial.println(vin);
     accuml = 0;
     delay(100);
}
