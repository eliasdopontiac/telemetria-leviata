#include "Arduino.h"
#include "VeDirectFrameHandler.h"

// Define os pinos de comunicação serial
#define rxPin 4  // Pino RX
#define txPin 5  // Pino TX

VeDirectFrameHandler myve;

// hex frame callback function
void HexCallback(const char* buffer, int size, void* data) {
  char tmp[100];
  if (size < 100) {
    memcpy(tmp, buffer, size * sizeof(char));
    tmp[size] = 0;
    Serial.print("received hex frame: ");
    Serial.println(tmp);
  } else {
    Serial.println("Error: buffer size too large");
  }
}

// log helper
void LogHelper(const char* module, const char* error) {
  Serial.print(module);
  Serial.print(": ");
  Serial.println(error);
}

void setup() {
  Serial.begin(115200);

  // Inicializa a comunicação serial
  Serial1.begin(19200, SERIAL_8N1, rxPin, txPin);
  Serial.println("DEBUG-setup");

  // Adiciona o callback hex protocol
  myve.addHexCallback(&HexCallback, (void*)42);
}

void loop() {
  ReadVEData();
  EverySecond();
}

void ReadVEData() {
  while (Serial1.available()) {
    myve.rxData(Serial1.read());
  }
}

void EverySecond() {
  static unsigned long prev_millis;

  if (millis() - prev_millis > 1500) {
    PrintData();
    prev_millis = millis();
  }
}

void PrintData() {
  for (int i = 15; i <= 17; i++) {
    if (i == 15 || i == 16) {
      Serial.print(myve.veName[i]);
      Serial.print("= ");
      Serial.println(atof(myve.veValue[i]) / 1000);
    }
    if (i == 17) {
      Serial.print(myve.veName[i]);
      Serial.print("= ");
      Serial.println(atof(myve.veValue[i]));
    }
  }
}
