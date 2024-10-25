#include <esp_now.h>
#include <WiFi.h>

#define botaoPin 27

// Endereço MAC do receptor (ESP32 escravo)
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

// Estrutura de exemplo para enviar dados
typedef struct struct_message {
  char status[15]; // Tamanho suficiente para "bombaligada" ou "bombadesligada"
} struct_message;

// Dados a serem enviados
struct_message myData;

esp_now_peer_info_t peerInfo;

// Função de callback quando os dados são enviados
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nÚltimo status de envio do pacote:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Sucesso" : "Falha");
}
 
void setup() {
  // Inicializa o Monitor Serial
  Serial.begin(115200);
  
  // Configura o pino do botão como entrada
  pinMode(botaoPin, INPUT);
 
  // Configura o dispositivo como Estação Wi-Fi
  WiFi.mode(WIFI_STA);

  // Inicializa o ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Erro ao inicializar ESP-NOW");
    return;
  }

  // Registra a função de callback para o status do envio
  esp_now_register_send_cb(OnDataSent);
  
  // Configura informações do peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Adiciona o peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Falha ao adicionar o peer");
    return;
  }

  Serial.println("Peer adicionado com sucesso");
}
 
void loop() {
  // Define os valores a serem enviados com base no estado do botão
  if (digitalRead(botaoPin)) {
    strcpy(myData.status, "bombaligada");
  } else {
    strcpy(myData.status, "bombadesligada");
  }
  
  // Envio da mensagem via ESP-NOW
  static unsigned long prev_millis = 0;

  if (millis() - prev_millis > 1000) {
    esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
    prev_millis = millis();
    
    if (result == ESP_OK) {
      Serial.println("Enviado com sucesso");
    } else {
      Serial.print("Erro ao enviar os dados: ");
      Serial.println(result);
    }
  }

  // Delay para enviar a cada 2 segundos
  //delay(2000);
}
