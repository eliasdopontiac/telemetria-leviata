/*
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp-now-esp32-arduino-ide/
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*/

#include <esp_now.h>
#include <WiFi.h>

// Pino de controle para a bomba
const int bombaPin = 26;

// Structure example to receive data
typedef struct struct_message {
    char status[15];
} struct_message;

// Create a struct_message called myData
struct_message myData;

// callback function that will be executed when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&myData, incomingData, sizeof(myData));
  Serial.print("Bytes received: ");
  Serial.println(len);
  Serial.print("Status received: ");
  Serial.println(myData.status);

  // Verifica o status recebido e controla o pino da bomba
  if (strcmp(myData.status, "bombaligada") == 0) {
    digitalWrite(bombaPin, HIGH); // Liga a bomba
    Serial.println("Bomba ligada");
  } else {
    digitalWrite(bombaPin, LOW); // Desliga a bomba
    Serial.println("Bomba desligada");
  }
}
 
void setup() {
  // Inicializa o Monitor Serial
  Serial.begin(115200);
  
  // Configura o pino da bomba como saída
  pinMode(bombaPin, OUTPUT);
  digitalWrite(bombaPin, LOW); // Garante que a bomba comece desligada
  
  // Set device as a Wi-Fi Station
  WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  
  // Once ESPNow is successfully Init, register the callback function
  esp_now_register_recv_cb(OnDataRecv);
}
 
void loop() {
  // Verificar se há dados na Serial
  if (Serial.available() > 0) {
    // Ler o texto da Serial
    String serialData = Serial.readString();
    
    // Comparar com "bomba ligada"
    if (serialData.indexOf("bomba ligada") != -1) {
      digitalWrite(bombaPin, HIGH); // Liga a bomba
      Serial.println("Bomba ligada via Serial");
    }
  }
  
  // No specific tasks needed in the loop since all functionality is in the callback
}
