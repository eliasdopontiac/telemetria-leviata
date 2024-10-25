// EmonLibrary examples openenergymonitor.org, Licence GNU GPL V3

#include "EmonLib.h"                   // Include Emon Library
EnergyMonitor emon1;                   // Create an instance
float current = 0.0;
void setup()
{  
  Serial.begin(9600);
  
  emon1.current(35, 14);             // Current: input pin, calibration. 2000/33 = 60.6
}

void loop()
{
  double Irms = emon1.calcIrms(1480);  // Calculate Irms only
  
  //Serial.println(Irms);		       // Irms
  Serial.print("Current: ");
  current = (1/2.6)*Irms+2.643;
  Serial.println(current);
}
