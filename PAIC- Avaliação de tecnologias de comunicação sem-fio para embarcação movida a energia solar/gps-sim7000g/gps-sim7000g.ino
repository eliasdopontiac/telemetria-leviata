// Set serial for debug console (to the Serial Monitor, default speed 115200)
#define SerialMon Serial

// Set serial for AT commands (to the module)
// Use Hardware Serial on Mega, Leonardo, Micro
#define SerialAT Serial1

#define TINY_GSM_MODEM_SIM7000
#define TINY_GSM_RX_BUFFER 1024 // Set RX buffer to 1Kb
#define SerialAT Serial1

// See all AT commands, if wanted
// #define DUMP_AT_COMMANDS

// set GSM PIN, if any
#define GSM_PIN ""

// Your GPRS credentials, if any
const char apn[]  = "claro.com.br";     //SET TO YOUR APN
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";

#include <TinyGsmClient.h>
#include <SPI.h>
#include <SD.h>
#include <Ticker.h>
#include <WiFi.h>
#include <FirebaseESP32.h>

// Defina as credenciais Wi-Fi e Firebase
#define WIFI_SSID "ELIAS 2G"
#define WIFI_PASSWORD "2214399980"
#define FIREBASE_HOST "teste-de-telemetria-default-rtdb.firebaseio.com" // Sem "https://"
#define FIREBASE_AUTH "7fFhVIGoDCEyMbNJvik7Dj1A4huj2fANlHO7ZqCQ"

// Inicialize as variáveis do Firebase
FirebaseData firebaseData;
FirebaseConfig config;
FirebaseAuth auth;

#ifdef DUMP_AT_COMMANDS
#include <StreamDebugger.h>
StreamDebugger debugger(SerialAT, SerialMon);
TinyGsm modem(debugger);
#else
TinyGsm modem(SerialAT);
#endif

#define uS_TO_S_FACTOR      1000000ULL  // Conversion factor for micro seconds to seconds
#define TIME_TO_SLEEP       60          // Time ESP32 will go to sleep (in seconds)

#define UART_BAUD           9600
#define PIN_DTR             25
#define PIN_TX              27
#define PIN_RX              26
#define PWR_PIN             4

#define SD_MISO             2
#define SD_MOSI             15
#define SD_SCLK             14
#define SD_CS               13
#define LED_PIN             12

void enableGPS(void)
{
    // Set Modem GPS Power Control Pin to HIGH ,turn on GPS power
    // Only in version 20200415 is there a function to control GPS power
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

void setup()
{
    // Set console baud rate
    SerialMon.begin(115200);

    delay(10);

    // Set LED OFF
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    modemPowerOn();

    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);
    delay(10000);
  
  // Conecte ao Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado ao Wi-Fi");

  // Configurar Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;

  // Inicializar Firebase
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  enableGPS();

}

void loop()
{
    if (!modem.testAT()) {
        Serial.println("Failed to restart modem, attempting to continue without restarting");
        modemRestart();
        return;
    }
    


    float lat,  lon, speed;
        if (modem.getGPS(&lat, &lon,&speed)) {
           Serial.println("The blue indicator light flashes to indicate positioning.");
            Serial.print("latitude:"); Serial.println(lat);
            Serial.print("longitude:"); Serial.println(lon);
            Serial.print("velocidade:"); Serial.println(speed);
        digitalWrite(LED_PIN, !digitalRead(LED_PIN));
        // Envie dados para o Firebase
        String latPath = "/gpsData/latitude";
        String lonPath = "/gpsData/longitude";
        String speedPath = "/gpsData/Velocidade";
        delay(2000);
          if (Firebase.setFloat(firebaseData, latPath, lat) &&
              Firebase.setFloat(firebaseData, lonPath, lon)&&
              Firebase.setFloat(firebaseData, speedPath, speed)) {
            Serial.println("Dados enviados com sucesso.");
          } else {
            Serial.println("Erro ao enviar dados: " + firebaseData.errorReason());
          }
    }
}