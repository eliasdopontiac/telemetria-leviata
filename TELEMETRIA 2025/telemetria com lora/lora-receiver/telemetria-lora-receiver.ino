// Rascunho do Recetor LoRa: Recebe dados, decodifica e publica no MQTT
#include <SPI.h>
#include <LoRa.h>
#include <HardwareSerial.h>
#include <WiFi.h>
#include <PubSubClient.h>

// --- LoRa ---
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26
#define BAND 915E6

// --- WiFi / MQTT ---
#define WIFI_SSID "telemetria"
#define WIFI_PASSWORD "leviata1"
const char *MQTTServer = "test.mosquitto.org";
const int MQTTPort = 1883;
const char* BMVTopic = "BMV";
const char* CTRLTopic = "Controladora";
const char* GPSTopic = "GPS";
const char* LOGTopic = "device/log";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

// --- Estruturas de dados para o recetor ---
// Estas estruturas devem ser idênticas às do transmissor
typedef struct {
  float bmv_T;
  float bmv_I;
  float bmv_P;
  float gps_lat;
  float gps_lon;
  float gps_speed_kmh;
} BmvPacket;

typedef struct {
  float gps_lat;
  float gps_lon;
  float gps_speed_nos;
  float ctrl_volt;
  float ctrl_line_current;
  float ctrl_motor_temp_c;
  float ctrl_rpm;
} FardriverPacket;

// --- Variáveis Globais ---
BmvPacket bmvData;
FardriverPacket fardriverData;
char messageType = ' ';
bool dataReceived = false;

// --- Protótipos ---
void connectToWiFi();
void connectToMQTT();
void reconnectToBrokerMQTT();
void mqttLog(const char* msg);
void onReceive(int packetSize);
void publishReceivedData();

// ---------------------------------------------------
// Funções de Conexão WiFi / MQTT
// ---------------------------------------------------
void connectToWiFi() {
  Serial.println("Tentando conectar ao WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    if (millis() - start > 15000) break;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi conectado!");
  } else {
    Serial.println("Falha na conexão WiFi.");
  }
}

void connectToMQTT() {
  client.setServer(MQTTServer, MQTTPort);
}

void reconnectToBrokerMQTT() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  unsigned long start = millis();
  while (!client.connected()) {
    Serial.println("Tentando conectar ao MQTT...");
    if (client.connect("LoRa_Receiver")) {
      Serial.println("MQTT conectado!");
      mqttLog("MQTT conectado");
      break;
    } else {
      Serial.print("Falha na conexão MQTT, RC: ");
      Serial.print(client.state());
      Serial.println(". Tentando novamente em 2 segundos...");
      delay(2000);
      if (millis() - start > 30000) break;
    }
  }
}

// ---------------------------------------------------
// Funções auxiliares
// ---------------------------------------------------
void mqttLog(const char* msg) {
  if (client.connected()) {
    client.publish(LOGTopic, msg);
  }
}

// ---------------------------------------------------
// Callback para a recepção de pacotes LoRa
// ---------------------------------------------------
void onReceive(int packetSize) {
  if (packetSize == 0) return;

  // Lê o primeiro byte para identificar o tipo de pacote
  messageType = (char)LoRa.read();
  
  if (messageType == 'B' && packetSize == sizeof(BmvPacket) + 1) {
    LoRa.readBytes((uint8_t*)&bmvData, sizeof(BmvPacket));
    dataReceived = true;
    Serial.println("Pacote BMV recebido!");
  } else if (messageType == 'F' && packetSize == sizeof(FardriverPacket) + 1) {
    LoRa.readBytes((uint8_t*)&fardriverData, sizeof(FardriverPacket));
    dataReceived = true;
    Serial.println("Pacote Fardriver recebido!");
  } else {
    Serial.print("Pacote de tipo ou tamanho inválido. ");
    Serial.print("Tamanho esperado: ");
    if(messageType == 'B') Serial.print(sizeof(BmvPacket)+1);
    else if (messageType == 'F') Serial.print(sizeof(FardriverPacket)+1);
    else Serial.print("?");
    Serial.print(", recebido: ");
    Serial.println(packetSize);
  }
}

// ---------------------------------------------------
// Publica dados recebidos no MQTT
// ---------------------------------------------------
void publishReceivedData() {
  char buf[256];
  
  Serial.print("Publicando dados... Tipo: ");
  Serial.println(messageType);

  if (messageType == 'B') {
    snprintf(buf, sizeof(buf), "{\"Tensao\":%.2f,\"Corrente\":%.3f,\"Potencia\":%.2f}", bmvData.bmv_T, bmvData.bmv_I, bmvData.bmv_P);
    client.publish(BMVTopic, buf);

    // CORREÇÃO: Usa a chave "Vel_KMH" para o pacote BMV
    snprintf(buf, sizeof(buf), "{\"Lat\":%.6f,\"Lon\":%.6f,\"Vel_KMH\":%.2f}", bmvData.gps_lat, bmvData.gps_lon, bmvData.gps_speed_kmh);
    client.publish(GPSTopic, buf);

  } else if (messageType == 'F') {
    snprintf(buf, sizeof(buf), "{\"Voltage\":%.1f,\"LineCurrent\":%.2f,\"MotorTempC\":%.1f,\"RPM\":%.1f}", fardriverData.ctrl_volt, fardriverData.ctrl_line_current, fardriverData.ctrl_motor_temp_c, fardriverData.ctrl_rpm);
    client.publish(CTRLTopic, buf);

    // CORREÇÃO: Altera a chave para "Vel_NOS" para o pacote Fardriver
    snprintf(buf, sizeof(buf), "{\"Lat\":%.6f,\"Lon\":%.6f,\"Vel_NOS\":%.2f}", fardriverData.gps_lat, fardriverData.gps_lon, fardriverData.gps_speed_nos);
    client.publish(GPSTopic, buf);
  }
}

// ---------------------------------------------------
// Configuração (setup)
// ---------------------------------------------------
void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ;
  }
  Serial.println("Iniciando recetor...");

  // Inicializa LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  if (!LoRa.begin(BAND)) {
    Serial.println("Falha na inicialização do LoRa!");
    for(;;);
  }
  LoRa.onReceive(onReceive);
  LoRa.receive();
  Serial.println("LoRa OK!");

  // Configuração do WiFi + MQTT
  connectToWiFi();
  connectToMQTT();
  LoRa.setTxPower(20);
  LoRa.setSpreadingFactor(12);


}

// ---------------------------------------------------
// Loop principal (não-bloqueante)
// ---------------------------------------------------
void loop() {
  // Mantém o MQTT funcionando / reconecta se necessário
  if (!client.connected()) reconnectToBrokerMQTT();
  client.loop();

  // Publica dados se um pacote foi recebido
  if (dataReceived) {
    Serial.println("Dados LoRa recebidos e prontos para publicação.");
    publishReceivedData();
    dataReceived = false;
  }
}