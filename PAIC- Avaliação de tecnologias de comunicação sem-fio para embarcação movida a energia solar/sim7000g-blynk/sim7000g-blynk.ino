/* Fill-in your Template ID (only if using Blynk.Cloud) */
#define BLYNK_TEMPLATE_ID "TMPL2-9lEWNW0"
#define BLYNK_TEMPLATE_NAME "paic"
#define BLYNK_AUTH_TOKEN "arOQzjoCgTzMjC_XnMjalcsvAI8xhKtK"
// Select your modem:
#define TINY_GSM_MODEM_SIM7000
#define GSM_PIN ""
#define SerialAT Serial1
#define DUMP_AT_COMMANDS


// Default heartbeat interval for GSM is 60
// If you want override this value, uncomment and set this option:
//#define BLYNK_HEARTBEAT 30

#include <TinyGsmClient.h>
#include <BlynkSimpleTinyGSM.h>

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Ticker.h>

// Your GPRS credentials
// Leave empty, if missing user or pass
char apn[]  = "claro.com.br";
char gprsUser[] = "claro";
char gprsPass[] = "claro";
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
void sendGPS()
{
  enableGPS();
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
void qualidadeSINAL(void){
    float sinal = modem.getSignalQuality();
    Serial.println("Signal quality: " + String(sinal));
    Blynk.virtualWrite(V3,sinal);
    }

void setup()
{
    Serial.begin(115200); // Set console baud rate
    delay(100);

    // Set LED OFF
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    // Starting the machine requires at least 1 second of low level, and with a level conversion, the levels are opposite
    delay(1000);
    digitalWrite(PWR_PIN, LOW);
    Serial.println("\nesperando...");

    delay(1000);

    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);


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

    bool res = modem.setNetworkMode(13);
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
    res = modem.setPreferredMode(1);
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
     modem.sendAT("+CBANDCFG=\"CAT-M\",8 ");
     if (modem.waitResponse(10000L) != 1) {
         DBG(" +CBANDCFG=\"CAT-M\" ");
     }
     delay(200);

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

    Blynk.begin(BLYNK_AUTH_TOKEN, modem, apn, gprsUser, gprsPass);
    }
}
void loop(){
    Blynk.run();
    sendGPS();
    qualidadeSINAL();
    sendBattery();
    delay(3000);
    }