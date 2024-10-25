void loop_mppt()
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
        Serial.print(atof(correntebateria));
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
        Serial.print(atof(tensaobateria));
        Serial.println("V");
     }

     else if (label == "VPV")        //TENSÃO DO PAINEL                    
     {
        val.toCharArray(buf, sizeof(buf));
        float meetwaarde = atof(buf);
        meetwaarde=meetwaarde/1000;
        dtostrf(meetwaarde, len, 2, tensaopainel);
        tensaopainel[len] = ' '; tensaopainel[len+1] = 0; 
        Serial.print("Tensão do painel: "); 
        Serial.print(atof(tensaopainel));
        Serial.println("V");
     }

         
     else if (label == "PPV")      //POTENCIA PAINEL                 
     {
        val.toCharArray(buf, sizeof(buf));                    
        meetwaarde = atof(buf);                               
        dtostrf(meetwaarde, len, 0, potenciapainel);          
        potenciapainel[len] = ' '; potenciapainel[len+1] = 0; 
        Serial.print("Potencia do painel: "); 
        Serial.print(atof(potenciapainel));
        Serial.println("W");
       
     }

      
     else if (label == "H23")     //POTENCIA MAXIMA DE ONTEM
     {
        val.toCharArray(buf, sizeof(buf));
        meetwaarde = atof(buf);
        dtostrf(meetwaarde, len, 0, potenciamaximaontem);
        potenciamaximaontem[len] = ' '; potenciamaximaontem[len+1] = 0;
        Serial.print("Potencia máxima de ontem: ");
        Serial.print(atof(potenciamaximaontem));
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
        Serial.print(atof(rendimentoontem));
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
        Serial.print(atof(rendimentohoje));
        Serial.println("kWh");
     }

  }
