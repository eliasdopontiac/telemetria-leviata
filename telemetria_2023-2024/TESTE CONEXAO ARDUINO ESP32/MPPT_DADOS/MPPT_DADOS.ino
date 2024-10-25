/* Connections:
    MPPT pin     MPPT        Arduino     Arduino pin
    1            GND         GND         GND
    2            RX          TX          -              nao usar!
    3            TX          RX          19 (MEGA)
    4            Power+      none        -              nao usar!
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

void setup(void)  
{

  Serial.begin(19200);
  Serial1.begin(19200);// Start communication with the MPPT controller, on the MEGA communication is through serial port 1

} 

void loop() 
{
  if (Serial1.available())
   {
        label = Serial1.readStringUntil('\t');                // this is the actual line that reads the label from the MPPT controller
        val = Serial1.readStringUntil('\r\r\n');              // this is the line that reads the value of the label

     if (label == "I")                                        // I chose to select certain paramaters that were good for me. check the Victron whitepaper for all labels.
     {                                                        // In this case I chose to read charging current
        val.toCharArray(buf, sizeof(buf));                    // conversion of val to a character array. Don't ask me why, I saw it in one of the examples of Adafruit and it works.
        float meetwaarde = atof(buf);                         // conversion to float
        meetwaarde = meetwaarde/1000;                         // calculating the correct value, see the Victron whitepaper for details. The value of label I is communicated in milli amps.
        dtostrf(meetwaarde, len, 2, correntebateria);              // conversion of calculated value to string
        correntebateria[len] = ' '; correntebateria[len+1] = 0;
        Serial.print("Corrente da Bateria: ");
        Serial.print(atoi(correntebateria));
        Serial.println("A");
     }
     
     else if (label == "V")        //TENSÃO DA BATERIA                    
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atof(buf);
        meetwaarde=meetwaarde/1000;
        dtostrf(meetwaarde, len, 2, tensaobateria);
        tensaobateria[len] = ' '; tensaobateria[len+1] = 0;
        Serial.print("Tensão da bateria: "); 
        Serial.print(atoi(tensaobateria));
        Serial.println("V");
     }
     
     else if (label == "IL")                                       
     {                                                        
        val.toCharArray(buf, sizeof(buf));                    
        float meetwaarde = atof(buf);                         
        meetwaarde = meetwaarde/1000;                         
        dtostrf(meetwaarde, len, 2, correntepainel);             
        correntepainel[len] = ' '; correntepainel[len+1] = 0;
        Serial.print("Corrente do Painel: ");
        Serial.print(atoi(correntepainel));
        Serial.println("A");
      }
     else if (label == "VPV")        //TENSÃO DO PAINEL                    
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atof(buf);
        meetwaarde=meetwaarde/1000;
        dtostrf(meetwaarde, len, 2, tensaopainel);
        tensaopainel[len] = ' '; tensaopainel[len+1] = 0; 
        Serial.print("Tensão do painel: "); 
        Serial.print(atoi(tensaopainel));
        Serial.println("V");
     }

         
     else if (label == "PPV")      //POTENCIA PAINEL                 
     {
        val.toCharArray(buf, sizeof(buf));                    
        meetwaarde = atof(buf);                               
        dtostrf(meetwaarde, len, 0, potenciapainel);          
        potenciapainel[len] = ' '; potenciapainel[len+1] = 0; 
        Serial.print("Potencia do painel: "); 
        Serial.print(atoi(potenciapainel));
        Serial.println("W");
     }

     else if (label == "H23")     //POTENCIA MAXIMA DE ONTEM
     {
        val.toCharArray(buf, sizeof(buf));
        meetwaarde = atof(buf);
        dtostrf(meetwaarde, len, 0, potenciamaximaontem);
        potenciamaximaontem[len] = ' '; potenciamaximaontem[len+1] = 0;
        Serial.print("Potencia máxima de ontem: ");
        Serial.print(atoi(potenciamaximaontem));
        Serial.println("W");
        Serial.println("-------------------");
     } 
     
     else if (label == "H22")     //RENDIMENTO ONTEM
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atof(buf);
        meetwaarde=meetwaarde/100;
        dtostrf(meetwaarde, len, 2, rendimentoontem);
        rendimentoontem[len] = ' '; rendimentoontem[len+1] = 0;
        Serial.print("Rendimento de ontem: ");
        Serial.print(atoi(rendimentoontem));
        Serial.println("kWh");
     }
     else if (label == "H20")     //RENDIMENTO HOJE
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atof(buf);
        meetwaarde=meetwaarde/100;
        dtostrf(meetwaarde, len, 2, rendimentohoje);
        rendimentohoje[len] = ' '; rendimentohoje[len+1] = 0;
        Serial.print("Rendimento de hoje: ");
        Serial.print(atoi(rendimentohoje));
        Serial.println("kWh");
     }

   }
}
