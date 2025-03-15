//template blynk
#define BLYNK_TEMPLATE_ID "TMPL2-9lEWNW0"
#define BLYNK_TEMPLATE_NAME "paic"
#define BLYNK_AUTH_TOKEN "arOQzjoCgTzMjC_XnMjalcsvAI8xhKtK"

//seleção do modem
#define TINY_GSM_MODEM_SIM7000
#define GSM_PIN ""
#define SerialAT Serial1
#define DUMP_AT_COMMANDS


#include <TinyGsmClient.h>
//#include <BlynkSimpleTinyGSM.h>
#include <BlynkSimpleEsp32.h>
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Ticker.h>
#include <WiFi.h>

// Defina as credenciais Wi-Fi
#define WIFI_SSID "elias do pontiac"
#define WIFI_PASSWORD "morangos"


#ifdef DUMP_AT_COMMANDS  // if enabled it requires the streamDebugger lib
#include <StreamDebugger.h>
StreamDebugger debugger(SerialAT, Serial);
TinyGsm modem(debugger);
#else
TinyGsm modem(SerialAT);
#endif

#define SerialAT Serial1
#define UART_BAUD   115200
#define PIN_DTR     25
#define PIN_TX      27
#define PIN_RX      26
#define PWR_PIN     4
#define LED_PIN     12
#define BAT_ADC     35 //piino da bateria


bool reply = false;

int counter, lastIndex, numberOfPieces = 24;
String pieces[24], input;

void enableGPS(void)
{
    // Set Modem GPS Power Control Pin to HIGH ,turn on GPS power
    modem.sendAT("+CGPIO=0,48,1,1");
    if (modem.waitResponse(10000L) != 1) {
        DBG("Set GPS Power HIGH Failed");
    }
    modem.enableGPS();
}

void disableGPS(void)
{
    // Set Modem GPS Power Control Pin to LOW ,turn off GPS power
    // Only in version 20200415 is there a function to control GPS power
    modem.sendAT("+CGPIO=0,48,1,0");
    if (modem.waitResponse(10000L) != 1) {
        DBG("Set GPS Power LOW Failed");
    }
    modem.disableGPS();
}
void modemPowerOn()
{
    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    delay(1000);    //Datasheet Ton mintues = 1S
    digitalWrite(PWR_PIN, LOW);
}

void modemPowerOff()
{
    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    delay(1500);    //Datasheet Ton mintues = 1.2S
    digitalWrite(PWR_PIN, LOW);
}


void modemRestart()
{
    modemPowerOff();
    delay(1000);
    modemPowerOn();
}
void sendGPS(){
float lat,  lon, speed;
        if (modem.getGPS(&lat, &lon,&speed)) {
           Serial.println("The blue indicator light flashes to indicate positioning.");
            Serial.print("latitude:"); Serial.println(lat);
            Serial.print("longitude:"); Serial.println(lon);
            Serial.print("velocidade:"); Serial.println(speed);
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    }
    // You can send any value at any time.
    // Please don't send more that 10 values per second.

    Blynk.virtualWrite(V0, speed);
    Blynk.virtualWrite(V1, lat);
    Blynk.virtualWrite(V2, lon);
}

float readBattery(uint8_t pin)
{
    int vref = 1100;
    uint16_t volt = analogRead(pin);
    float battery_voltage = ((float)volt / 4095.0) * 2.0 * 3.3 * (vref);
    return battery_voltage;
}
void sendBattery(){

  float mv = readBattery(BAT_ADC);
  Blynk.virtualWrite(V4, ((mv / 4200) * 100));
  Serial.print("tensão da bateria = ");
  Serial.println(mv);

}
void setup() {
  Serial.begin(115200);  // Comunicação com o PC

  // Conectar ao Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int timeout = 10000;  // Timeout de 10 segundos
  unsigned long startAttemptTime = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < timeout) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Falha na conexão Wi-Fi");
  } else {
    Serial.println("Conectado ao Wi-Fi");
  }

  modemPowerOn();
    // Restart takes quite some time
    // To skip it, call init() instead of restart()
    Serial.println("iniciando modem...");
    if (!modem.restart()) {
        Serial.println("Failed to restart modem, attempting to continue without restarting");
    }

    String name = modem.getModemName();
    delay(500);
    Serial.println("Modem Name: " + name);
    
    if ( GSM_PIN && modem.getSimStatus() != 3 ) {
        modem.simUnlock(GSM_PIN);
        modem.sendAT("+CFUN=0");
    if (modem.waitResponse(10000L) != 1) {
        DBG(" +CFUN=0  false ");
    }
    }
    delay(200);

  // Inicializar Blynk
  Blynk.begin(BLYNK_AUTH_TOKEN, WIFI_SSID, WIFI_PASSWORD);
}
void loop(){
    Blynk.run();
    sendGPS();
    sendBattery();
    delay(500);
}




