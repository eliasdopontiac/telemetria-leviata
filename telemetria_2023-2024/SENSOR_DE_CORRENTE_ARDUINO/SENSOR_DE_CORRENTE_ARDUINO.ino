/* ==============================================================================================

     WR Kits & Usina Info

     Sensor de Corrente ACS758  050B


     Autor: Eng. Wagner Rambo
     Data: Abril de 2019

     Compilador: Arduino IDE 1.8.4


============================================================================================== */


// ==============================================================================================
// --- Mapeamento de Hardware ---
#define    c_sens    A0


// ==============================================================================================
// --- Variáveis Globais ---
float   volt, 
        c_value;


// ==============================================================================================
// --- Configurações Iniciais ---
void setup() 
{
    pinMode(c_sens, INPUT);
    Serial.begin(9600);

    
} //end setup


// ==============================================================================================
// --- Loop Infinito ---
void loop() 
{

  //calcula tensão
  volt = (5.0 / 1023.0)*analogRead(c_sens);// Read the voltage from sensor


  //calcula corrente (ACS758 050B varia 40mV / A)
  c_value = volt/0.04;


  //Imprime dados via serial
  Serial.print("V: ");
  Serial.print(volt,3);
  Serial.print("V   |   I: ");
  Serial.print(c_value,2); 
  Serial.println("A");
  delay(741);


} //end loop
