#define TINY_GSM_MODEM_SIM7000
#define SerialMon Serial
#define SerialAT Serial1
#define TINY_GSM_DEBUG SerialMon
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false

#define GSM_PIN ""

// credenciais GPRS
const char apn[]      = "claro.com.br";
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";
// credenciais do WIFI
const char wifiSSID[] = "UEA-EDU";
const char wifiPass[] = "12072022";
// credenciais do mqtt
const char *broker = "test.mosquitto.org";
const int mqtt_port = 1883;

#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Ticker.h>
#include <HardwareSerial.h>

//------------------------lcd--------------------
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
//------------------------lcd--------------------

#include <EmonLib.h>


#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_SDA 21
#define OLED_SCK 22
#define OLED_ADDR 0x3C  // Endereço I2C do display

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

#if TINY_GSM_USE_GPRS && not defined TINY_GSM_MODEM_HAS_GPRS
#undef TINY_GSM_USE_GPRS
#undef TINY_GSM_USE_WIFI
#define TINY_GSM_USE_GPRS false
#define TINY_GSM_USE_WIFI true
#endif
#if TINY_GSM_USE_WIFI && not defined TINY_GSM_MODEM_HAS_WIFI
#undef TINY_GSM_USE_GPRS
#undef TINY_GSM_USE_WIFI
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false
#endif

#ifdef DUMP_AT_COMMANDS
#include <StreamDebugger.h>
StreamDebugger debugger(SerialAT, SerialMon);
TinyGsm        modem(debugger);
#else
TinyGsm        modem(SerialAT);
#endif
TinyGsmClient client(modem);
PubSubClient  mqtt(client);

Ticker tick;

#define uS_TO_S_FACTOR 1000000ULL  // Conversion factor for micro seconds to seconds
#define TIME_TO_SLEEP  60          // Time ESP32 will go to sleep (in seconds)

#define UART_BAUD   115200
#define PIN_DTR     25
#define PIN_TX      27
#define PIN_RX      26
#define PWR_PIN     4

#define LED_PIN     12


//--------CONFIGURAÇÃO MPPT
#define RX_MPPT 34

int ledStatus = LOW;


bool reply = false;

int counter, lastIndex, numberOfPieces = 24;
String pieces[24], input;
unsigned long lastUpdateTime = 0;  // Variável para controlar o tempo
unsigned long updateInterval = 1000;  // Intervalo de 1 segundo (1000 ms)

uint32_t lastReconnectAttempt = 0;


void enableGPS(void)
{
    // Set Modem GPS Power Control Pin to HIGH ,turn on GPS power
    modem.sendAT("+CGPIO=0,48,1,1");
    if (modem.waitResponse(10000L) != 1) {
        DBG("Set GPS Power HIGH Failed");
    }
    modem.enableGPS();
    Serial.println("gps coletado");
}

void disableGPS(void)
{
    // Set Modem GPS Power Control Pin to LOW ,turn off GPS power
    modem.sendAT("+CGPIO=0,48,1,0");
    if (modem.waitResponse(10000L) != 1) {
        DBG("Set GPS Power LOW Failed");
    }
    modem.disableGPS();
}
void sendGPS() {
    float lat, lon, speed;
    
    if (modem.getGPS(&lat, &lon, &speed)) {
        Serial.println("ˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇGPSˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇˇ");
        Serial.println("O led azul indica recebimento do sinal");
        Serial.print("latitude:"); Serial.println(lat);
        Serial.print("longitude:"); Serial.println(lon);
        Serial.print("velocidade:"); Serial.println(speed);
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        
    Serial.println("^^^^^^^^^^^^^^^^^^^^GPS^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^");
    }

    // Converte a velocidade, se necessário
    float velocidade = speed * 1.043;

    // Publica cada variável em um tópico separado
    mqtt.publish("node-red/gps/latitude", String(lat, 4).c_str());
    mqtt.publish("node-red/gps/longitude", String(lon, 4).c_str());
    mqtt.publish("node-red/gps/velocidade", String(velocidade, 2).c_str());
}

void qualidadeSINAL(void){
    float sinal = modem.getSignalQuality();
    Serial.println("Signal quality: " + String(sinal));
        // Publica os dados no tópico MQTT
        mqtt.publish("node-red/Qsinal",String(sinal, 2).c_str());

    }
void mppt(){
}
void enviarmppt() {

  if (Serial2.available()) {
    String label = Serial2.readStringUntil('\t');           // leitura do label do MPPT
    String val = Serial2.readStringUntil('\r\r\n');         // leitura do valor do label

    if (label == "I") {  // Corrente da Bateria
      float corrente = val.toFloat() / 1000;  // Corrente em A
      Serial.print("Corrente da Bateria: ");
      Serial.print(corrente);
      Serial.println(" A");
      mqtt.publish("node-red/mppt/CorrenteBat", String(corrente, 4).c_str());
    }
    else if (label == "V") {  // Tensão da Bateria
      float tensao = val.toFloat() / 1000;  // Tensão em V
      Serial.print("Tensão da bateria: ");
      Serial.print(tensao);
      Serial.println(" V");
      mqtt.publish("node-red/mppt/TensaoBat", String(tensao, 4).c_str());
    }
    else if (label == "VPV") {  // Tensão do Painel
      float tensaoPainel = val.toFloat() / 1000;  // Tensão em V
      Serial.print("Tensão do painel: ");
      Serial.print(tensaoPainel);
      Serial.println(" V");
      mqtt.publish("node-red/mppt/TensaoPAINEL", String(tensaoPainel, 4).c_str());
    }
    else if (label == "PPV") {  // Potência do Painel
      float potencia = val.toFloat();  // Potência em W
      Serial.print("Potência do painel: ");
      Serial.print(potencia);
      Serial.println(" W");
      mqtt.publish("node-red/mppt/Potencia", String(potencia, 4).c_str());
  }
  Serial.println("^^^^^^^^^^^^^^^^^^^^^^mppt^^^^^^^^^^^^^^^^^^^^^^^^^^^^");
   static unsigned long prev_millis;
}

}


boolean mqttConnect()
{
    SerialMon.print("Connecting to ");
    SerialMon.print(broker);

    // Connect to MQTT Broker
    boolean status = mqtt.connect("GsmClientTest");
    if (status == false) {
        SerialMon.println(" fail");
        return false;
    }
    SerialMon.println(" CONECTADO LES GOOOO");
    return mqtt.connected();
    
}


void setup()
{
    // Set console baud rate
    Serial.begin(115200);
    Serial2.begin(19200, SERIAL_8N1, RX_MPPT, NULL); 
    delay(10);

    // Set LED OFF
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    delay(1000);
    digitalWrite(PWR_PIN, LOW);

    Serial.println("\espera...");
    Serial.println("\n----------------------------------");

    delay(1000);
    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);
    
    Wire.begin(OLED_SDA, OLED_SCK); 


 if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println(F("Falha ao inicializar o display OLED"));
    for (;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(30, 0);
  
  display.println(F("Leviata"));
  display.println(F("Conectado à ESP32"));
  display.display(); // Mostra no display
  display.clearDisplay();
  delay(3000);



    // Restart takes quite some time
    // To skip it, call init() instead of restart()
    Serial.println("Inicializando SIM7000G...");
    if (!modem.restart()) {
        Serial.println("Failed to restart modem, attempting to continue without restarting");
    }
/*  Preferred mode selection : AT+CNMP
          2 – Automatic
          13 – GSM Only
          14 – WCDMA Only
          38 – LTE Only
          48 – Any but LTE
          51 – GSM+LTE Only
    */
  String ret;
    //    do {
    //        ret = modem.setNetworkMode(2);
    //        delay(500);
    //    } while (ret != "OK");
    ret = modem.setNetworkMode(48);
    DBG("setNetworkMode:", ret);


    String name = modem.getModemName();
    DBG("Modem Name:", name);

    String modemInfo = modem.getModemInfo();
    DBG("Modem Info:", modemInfo);

#if TINY_GSM_USE_GPRS
    // Unlock your SIM card with a PIN if needed
    if (GSM_PIN && modem.getSimStatus() != 3) {
        modem.simUnlock(GSM_PIN);
    }
#endif

#if TINY_GSM_USE_WIFI
    // Os parâmetros de conexão Wi-Fi devem ser definidos antes de aguardar a rede
    SerialMon.print(F("Setting SSID/password..."));
    if (!modem.networkConnect(wifiSSID, wifiPass)) {
        SerialMon.println("falha!");
        delay(1000);
        return;
    }
    SerialMon.println(" sucesso");
#endif

    SerialMon.print("Waiting for network...");
    if (!modem.waitForNetwork()) {
        SerialMon.println(" fail");
        delay(100);
        return;
    }
    SerialMon.println(" success");

    if (modem.isNetworkConnected()) {
        SerialMon.println("Network connected");
    }

#if TINY_GSM_USE_GPRS
    // Os parâmetros de conexão GPRS geralmente são definidos após o registro da rede
    SerialMon.print(F("Conectando para: "));
    SerialMon.print(apn);
    if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
        SerialMon.println(" fail");
        delay(100);
        return;
    }
    SerialMon.println(" successo");

    if (modem.isGprsConnected()) {
        SerialMon.println(" conectado");
    }
#endif

    // MQTT Broker setup
    mqtt.setServer(broker, 1883);
    enableGPS();
    Serial.println("timer");
    delay(5000);

}

void loop()
{
    sendGPS();
    qualidadeSINAL();
    enviarmppt();
    delay(200);
    //Certifique-se de que ainda estamos registrados na rede
    if (!modem.isNetworkConnected()) {
        SerialMon.println("rede desconectada");
        if (!modem.waitForNetwork(180000L, true)) {
            SerialMon.println(" fail");
            delay(1000);
            return;
        }
        if (modem.isNetworkConnected()) {
            SerialMon.println(" rede reconectada");
        }

#if TINY_GSM_USE_GPRS
        // e certifique-se de que o GPRS/EPS ainda esteja conectado
        if (!modem.isGprsConnected()) {
            SerialMon.println(" disconnected!");
            SerialMon.print(F("Connecting to "));
            SerialMon.print(apn);
            if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
                SerialMon.println(" fail");
                delay(100);
                return;
            }
            if (modem.isGprsConnected()) {
                SerialMon.println("LTE reconnected");
            }
        }
#endif
    }

    if (!mqtt.connected()) {
        SerialMon.println("=== MQTT NÃO FOI CONECTADO ===");
        // Reconnect every 10 seconds
        uint32_t t = millis();
        if (t - lastReconnectAttempt > 10000L) {
            lastReconnectAttempt = t;
            if (mqttConnect()) {
                lastReconnectAttempt = 0;
            }
        }
        delay(100);
        return;
    }

    mqtt.loop();

}