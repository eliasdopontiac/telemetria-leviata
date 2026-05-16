/*
  Telemetria Leviatã v2026 - Simulador LilyGO (ESP32)
  -------------------------------------------------------
  REVERTIDO PARA HIVEMQ (Mais estável para ESP32)
*/

#include <WiFi.h>
#include <PubSubClient.h>

// --- CONFIGURAÇÕES DE REDE ---
const char* ssid = "NOME_DO_SEU_WIFI";
const char* password = "SENHA_DO_SEU_WIFI";

// Voltando para o HiveMQ
const char* mqtt_broker = "broker.hivemq.com"; 
const char* mqtt_topic = "barco/telemetria/LTE";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastTime = 0;
int packetSequence = 0;

void setup_wifi() {
  delay(100);
  Serial.print("\nConectando em: "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  int timeout = 0;
  while (WiFi.status() != WL_CONNECTED && timeout < 40) {
    delay(500); Serial.print("."); timeout++;
  }
  if(WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi OK!");
  } else {
    Serial.println("\nFalha no WiFi.");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("MQTT Connect (HiveMQ)...");
    String clientId = "LeviataBoat-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("SUCESSO!");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("ERRO rc=");
      Serial.print(client.state());
      Serial.println(" (tentando em 5s)");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_broker, mqtt_port);
  client.setBufferSize(1024); // Mantendo o buffer alto para o JSON
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  unsigned long now = millis();
  if (now - lastTime >= 1000) {
    lastTime = now;
    packetSequence++;

    // JSON com os dados que o seu Dashboard já entende
    String json = "{\"solar\":{\"tensao\":48.2,\"corrente\":5.0,\"pot\":241},";
    json += "\"bateria\":{\"soc\":98.5,\"tensao_bat\":53.1,\"corrente_liq\":-3.5},";
    json += "\"prop\":{\"rpm\":1500,\"i_motor\":8.5,\"t_motor\":45,\"t_ctrl\":38,\"fardriver_falha\":0},";
    json += "\"nav\":{\"vel\":15.5,\"lat\":-3.11902,\"lon\":-60.02173,\"gps_hora\":\"12:00:00\",\"gps_satelites\":10},";
    json += "\"sinal\":{\"lora\":-80,\"lte\":22,\"lora_pacotes\":" + String(packetSequence) + "}}";

    Serial.println(json); 
    client.publish(mqtt_topic, json.c_str());
  }
}
