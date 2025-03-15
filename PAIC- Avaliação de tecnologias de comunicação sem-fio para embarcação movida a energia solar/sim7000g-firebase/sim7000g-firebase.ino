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
#include <FirebaseESP32.h>

// Defina as credenciais Wi-Fi e Firebase
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

int counter, lastIndex, numberOfPieces = 24;
String pieces[24], input;


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
void verificarConexao() {
    // Inicializa o Firebase
    Firebase.begin(&config, &auth);
    
    // Adiciona uma verificação para confirmar a conexão
    if (Firebase.ready()) {
        Serial.println("Conexão com o Firebase estabelecida.");
    } else {
        Serial.println("Falha ao conectar ao Firebase.");
        // Você pode implementar um mecanismo de reconexão aqui, se necessário.
    }
}


void enviarGPS() {
    float lat, lon, speed;
    if (modem.getGPS(&lat, &lon, &speed)) {
        Serial.println("Posição obtida:");
        Serial.print("Latitude: "); Serial.println(lat);
        Serial.print("Longitude: "); Serial.println(lon);
        Serial.print("Velocidade: "); Serial.println(speed);
        
        String latPath = "/gpsData/latitude";
        String lonPath = "/gpsData/longitude";
        String speedPath = "/gpsData/velocidade";
        
        // Enviar dados para o Firebase
        if (Firebase.setFloat(firebaseData, latPath, lat) &&
            Firebase.setFloat(firebaseData, lonPath, lon) &&
            Firebase.setFloat(firebaseData, speedPath, speed)) {
            Serial.println("Dados enviados com sucesso.");
        } else {
            Serial.println("Erro ao enviar dados: " + firebaseData.errorReason());
        }
    } else {
        Serial.println("Falha ao obter dados GPS.");
    }
}

void qualidadeSINAL(void){
    float sinal = modem.getSignalQuality();
    String sinalPath = "/qualidade do sinal";
    Serial.println("Signal quality: " + String(sinal));
     if (Firebase.setFloat(firebaseData, sinalPath, sinal)){
      Serial.println("sinal enviado");
     }
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
    delay(200);

    /*
      2 Automatic
      13 GSM only
      38 LTE only
      51 GSM and LTE only
    * * * */

    bool res = modem.setNetworkMode(51);
    if (!res) {
        DBG("setNetworkMode  false ");
        return ;
    }
    delay(200);

    /*
      1 CAT-M
      2 NB-Iot
      3 CAT-M and NB-IoT
    * * */
    res = modem.setPreferredMode(3);
    if (!res) {
        DBG("setPreferredMode  false ");
        return ;
    }
    delay(200);

    /*AT+CBANDCFG=<mode>,<band>[,<band>…]
     * <mode> "CAT-M"   "NB-IOT"
     * <band>  The value of <band> must is in the band list of getting from  AT+CBANDCFG=?
     * For example, my SIM card carrier "NB-iot" supports B8.  I will configure +CBANDCFG= "Nb-iot ",8
     */
    /* modem.sendAT("+CBANDCFG=\"NB-IOT\",8 ");
     if (modem.waitResponse(10000L) != 1) {
         DBG(" +CBANDCFG=\"NB-IOT\" ");
     }
     delay(200);*/

    modem.sendAT("+CFUN=1");
    if (modem.waitResponse(10000L) != 1) {
        DBG(" +CFUN=1  false ");
    }
    delay(200);

    SerialAT.println("AT+CGDCONT?");
    delay(500);
    if (SerialAT.available()) {
        input = SerialAT.readString();
        for (int i = 0; i < input.length(); i++) {
            if (input.substring(i, i + 1) == "\n") {
                pieces[counter] = input.substring(lastIndex, i);
                lastIndex = i + 1;
                counter++;
            }
            if (i == input.length() - 1) {
                pieces[counter] = input.substring(lastIndex, i);
            }
        }
        // Reset for reuse
        input = "";
        counter = 0;
        lastIndex = 0;

        for ( int y = 0; y < numberOfPieces; y++) {
            for ( int x = 0; x < pieces[y].length(); x++) {
                char c = pieces[y][x];  //gets one byte from buffer
                if (c == ',') {
                    if (input.indexOf(": ") >= 0) {
                        String data = input.substring((input.indexOf(": ") + 1));
                        if ( data.toInt() > 0 && data.toInt() < 25) {
                            modem.sendAT("+CGDCONT=" + String(data.toInt()) + ",\"IP\",\"" + String(apn) + "\",\"0.0.0.0\",0,0,0,0");
                        }
                        input = "";
                        break;
                    }
                    // Reset for reuse
                    input = "";
                } else {
                    input += c;
                }
            }
        }
    } else {
        Serial.println("Failed to get PDP!");
    }


    Serial.println("\n\n\nWaiting for network...");
    if (!modem.waitForNetwork()) {
        delay(10000);
        return;
    }

    if (modem.isNetworkConnected()) {
        Serial.println("Network connected");
    }

    Serial.println("\n---Iniciando gprs---\n");
    Serial.println("Conectando: " + String(apn));
    if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
        delay(10000);
        return;
    }

    Serial.print("GPRS status: ");
    if (modem.isGprsConnected()) {
        Serial.println("connected");
    } else {
        Serial.println("not connected");
    }

    String ccid = modem.getSimCCID();
    Serial.println("CCID: " + ccid);

    String imei = modem.getIMEI();
    Serial.println("IMEI: " + imei);

    String cop = modem.getOperator();
    Serial.println("Operator: " + cop);

    IPAddress local = modem.localIP();
    Serial.println("Local IP: " + String(local));



  // Configurar Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;

  // Inicializar Firebase
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
  enableGPS();
    }
}
void loop(){
if (modem.isNetworkConnected()) {
        verificarConexao();
        enviarGPS();
        qualidadeSINAL();
    } else {
        Serial.println("Rede não conectada. Tentando reconectar...");
        modemRestart();
    }
    delay(10000); // Atraso para não sobrecarregar a rede
}