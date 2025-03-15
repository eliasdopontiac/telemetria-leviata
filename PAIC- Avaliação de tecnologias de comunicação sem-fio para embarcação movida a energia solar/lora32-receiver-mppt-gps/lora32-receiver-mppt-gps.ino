#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Bibliotecas para OLED Display
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Pinos para o LoRa
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

// Frequência do LoRa
#define BAND 915E6

// OLED pinos
#define OLED_SDA 4
#define OLED_SCL 15
#define OLED_RST 16
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define LOGO_HEIGHT 64
#define LOGO_WIDTH 128
#define buzzer_pin 23

// Configuração do WiFi e MQTT
const char* ssid = "UEA-EDU";  // WiFi
const char* password = "12072022";  // Senha do WiFi
const char* mqttServer = "broker.hivemq.com";  // Endereço do MQTT Broker
const int mqttPort = 1883;

// Tópicos MQTT
const char* mqttTopicSpeed = "Lora32/velocidade";
const char* mqttTopicRSSI = "Lora32/rssi";
const char* mqttTopicLostPackets = "Lora32/pacotes_perdidos";
const char* mqttTopicPacote = "Lora32/pacote";
const char* mqttTopicCorrenteBateria = "Lora32/CorrenteBat";
const char* mqttTopicTensaoBateria = "Lora32/TensaoBat";
const char* mqttTopicTensaoPV = "Lora32/TensaoPV";
const char* mqttTopicPotenciaPV = "Lora32/PotenciaPV";

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Variáveis LoRa e dados
String LoRaData;
int rssi = 0;  // RSSI
int packetCountReceived = 0;  // Número de pacotes recebidos
int packetCountLost = 0;  // Número de pacotes perdidos
int lastPacketReceived = 0;  // Último número de pacote recebido

// Variáveis para armazenar dados do MPPT
float correnteBateria = 0.0;
float tensaoBateria = 0.0;
float tensaoPainel = 0.0;
float potenciaPainel = 0.0;

void setup() {
  Serial.begin(115200);

  // Inicialização do OLED
  pinMode(OLED_RST, OUTPUT);
  digitalWrite(OLED_RST, LOW);
  delay(20);
  digitalWrite(OLED_RST, HIGH);
  Wire.begin(OLED_SDA, OLED_SCL);
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3c, false, false)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }

  // Conectar ao WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando ao WiFi...");
  }
  Serial.println("Conectado ao WiFi!");

  // Exibir logo do Leviatã
  logoleviata();

  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("LORA RECEIVER");
  display.print("WiFi conectado");
  display.display();

  // Inicialização do MQTT
  mqttClient.setServer(mqttServer, mqttPort);

  // Inicialização do LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  if (!LoRa.begin(BAND)) {
    Serial.println("Falha na inicialização do LoRa!");
    while (1);
  }
  Serial.println("LoRa inicializado!");

  display.setCursor(0, 20);
  display.println("LoRa inicializado!");
  display.display();

  // Configuração da potência e Spreading Factor (SF)
  int potencia = 20;
  LoRa.setTxPower(potencia);
  int sf = 12;  // Spreading Factor entre 6 e 12
  LoRa.setSpreadingFactor(sf);
  Serial.print("Spreading Factor configurado para: ");
  Serial.println(sf);

  pinMode(buzzer_pin, OUTPUT);
  digitalWrite(buzzer_pin, LOW);
}

void loop() {
  // Conectar ao MQTT se não estiver conectado
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();

  // Verificar pacotes LoRa
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Receber dados do LoRa
    Serial.print("Pacote recebido: ");
    digitalWrite(buzzer_pin, HIGH);
    delay(50);
    digitalWrite(buzzer_pin, LOW);
    while (LoRa.available()) {
      LoRaData = LoRa.readString();
      Serial.print(LoRaData);
    }

    // Obter RSSI do pacote
    rssi = LoRa.packetRssi();
    Serial.print(" com RSSI ");
    Serial.println(rssi);

    // Processar os dados recebidos
    processLoRaData(LoRaData);

    // Publicar dados via MQTT
    mqttClient.publish(mqttTopicSpeed, String(speed).c_str());
    mqttClient.publish(mqttTopicRSSI, String(rssi).c_str());
    mqttClient.publish(mqttTopicLostPackets, String(packetCountLost).c_str());
    mqttClient.publish(mqttTopicPacote, String(lastPacketReceived).c_str());
    mqttClient.publish(mqttTopicCorrenteBateria, String(correnteBateria).c_str());
    mqttClient.publish(mqttTopicTensaoBateria, String(tensaoBateria).c_str());
    mqttClient.publish(mqttTopicTensaoPV, String(tensaoPainel).c_str());
    mqttClient.publish(mqttTopicPotenciaPV, String(potenciaPainel).c_str());

    // Exibir dados no OLED
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("LORA RECEIVER");
    display.setCursor(0, 20);
    display.print("RSSI: ");
    display.print(rssi);
    display.setCursor(0, 30);
    display.print("Perda Pacotes: ");
    display.print(packetCountLost);
    display.setCursor(0, 40);
    display.print("Corrente: ");
    display.print(correnteBateria);
    display.print(" A");
    display.setCursor(0, 50);
    display.print("Tensão: ");
    display.print(tensaoBateria);
    display.print(" V");
    display.display();
  }
}

// Função para processar os dados recebidos do LoRa
void processLoRaData(String data) {
  // Extrair o número do pacote
  int packetNumber = data.substring(data.indexOf("Packet: ") + 8, data.indexOf(", Lat:")).toInt();

  // Atualizar contagem de pacotes recebidos e perdidos
  if (packetNumber == lastPacketReceived + 1) {
    packetCountReceived++;
    lastPacketReceived = packetNumber;
  } else {
    int lostPackets = packetNumber - lastPacketReceived - 1;
    packetCountLost += lostPackets;
    lastPacketReceived = packetNumber;
  }

  // Extrair dados do MPPT
  correnteBateria = getValue(data, "I: ", ',').toFloat();
  tensaoBateria = getValue(data, "V: ", ',').toFloat();
  tensaoPainel = getValue(data, "VPV: ", ',').toFloat();
  potenciaPainel = getValue(data, "PPV: ", '\0').toFloat();
}

// Função para extrair valores da string
String getValue(String data, String key, char separator) {
  int startIndex = data.indexOf(key) + key.length();
  int endIndex = data.indexOf(separator, startIndex);
  if (endIndex == -1) endIndex = data.length();
  return data.substring(startIndex, endIndex);
}

// Função para reconectar ao MQTT
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    Serial.println("Tentando conectar ao MQTT...");
    if (mqttClient.connect("LoraReceiverClient")) {
      Serial.println("Conectado ao MQTT!");
    } else {
      Serial.print("Falha, rc=");
      Serial.print(mqttClient.state());
      delay(5000);
    }
  }
}

// Função para exibir a logo do Leviatã
void logoleviata(void) {
  display.clearDisplay();
  display.drawBitmap(
    (display.width() - LOGO_WIDTH) / 2,
    (display.height() - LOGO_HEIGHT) / 2,
    epd_bitmap_Captura_de_tela_2025_01_19_163443, LOGO_WIDTH, LOGO_HEIGHT, 1);
  display.display();
  delay(5000);
  display.invertDisplay(false);
}