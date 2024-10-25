//RPM SENSOR
#define INTERRUPT_PIN 0   // Arduino Mega digital pin 2
volatile int interruptCount;
float rpm = 0;
float numpoles = 6;   //Change value to the number of magnets in the motor.

void setup() {
    Serial.begin(9600);

    // RPM COUNTER INIT
     pinMode(INTERRUPT_PIN, INPUT);
     attachInterrupt(INTERRUPT_PIN, interruptFired, CHANGE);
}

void loop(){

 checkRPM();

}

// Check RPM Function
void checkRPM() {
        noInterrupts() ;
        interruptCount = 0;  // set variable in critical section
        interrupts() ;
        delay (100);
        noInterrupts() ;
        int critical_rpm = interruptCount ;  // read variable in critical section 
        interrupts() ;
        rpm = ((critical_rpm)*(60))/(numpoles)*10;
        Serial.print("Motor RPMs : ");Serial.println(rpm);
       
   }

void interruptFired()
{
    interruptCount++;
}