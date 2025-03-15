//seleciona o modem
#define TINY_GSM_MODEM_SIM7000
#define GSM_PIN ""
#define SerialAT Serial1
#define DUMP_AT_COMMANDS

// Define the serial console for debug prints, if needed
#define TINY_GSM_DEBUG SerialMon

// Define how you're planning to connect to the internet
// These defines are only for this example; they are not needed in other code.
#define TINY_GSM_USE_GPRS true
#define TINY_GSM_USE_WIFI false


// credenciais do GPRS
const char apn[]      = "claro.com.br";
const char gprsUser[] = "claro";
const char gprsPass[] = "claro";


// MQTT details
const char *broker = "broker.hivemq.com";

const char *topicLed       = "GsmClientTest/led";
const char *topicInit      = "GsmClientTest/init";
const char *topicLedStatus = "GsmClientTest/ledStatus";


#include <TinyGsmClient.h>
#include <PubSubClient.h>
#include <Ticker.h>
#include <SPI.h>


// Just in case someone defined the wrong thing..
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


#define SerialAT Serial1
#define UART_BAUD   115200
#define PIN_DTR     25
#define PIN_TX      27
#define PIN_RX      26
#define PWR_PIN     4
#define LED_PIN     12
#define BAT_ADC     35 //piino da bateria



int ledStatus = LOW;

uint32_t lastReconnectAttempt = 0;

void mqttCallback(char *topic, byte *payload, unsigned int len)
{

    SerialMon.print("Message arrived [");
    SerialMon.print(topic);
    SerialMon.print("]: ");
    SerialMon.write(payload, len);
    SerialMon.println();

    // Only proceed if incoming message's topic matches
    if (String(topic) == topicLed) {
        ledStatus = !ledStatus;
        digitalWrite(LED_PIN, ledStatus);
        SerialMon.print("ledStatus:");
        SerialMon.println(ledStatus);
        mqtt.publish(topicLedStatus, ledStatus ? "1" : "0");

    }
}

boolean mqttConnect()
{
    SerialMon.print("Connecting to ");
    SerialMon.print(broker);

    // Connect to MQTT Broker
    boolean status = mqtt.connect("GsmClientTest");

    // Or, if you want to authenticate MQTT:
    // boolean status = mqtt.connect("GsmClientName", "mqtt_user", "mqtt_pass");

    if (status == false) {
        SerialMon.println(" fail");
        return false;
    }
    SerialMon.println(" success");
    mqtt.publish(topicInit, "GsmClientTest started");
    mqtt.subscribe(topicLed);
    return mqtt.connected();
}


void setup()
{
    // Set console baud rate
    Serial.begin(115200);
    delay(10);

    // Set LED OFF
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH);

    pinMode(PWR_PIN, OUTPUT);
    digitalWrite(PWR_PIN, HIGH);
    // Starting the machine requires at least 1 second of low level, and with a level conversion, the levels are opposite
    delay(1000);
    digitalWrite(PWR_PIN, LOW);
    Serial.println("\nWait...");

    delay(1000);

    SerialAT.begin(UART_BAUD, SERIAL_8N1, PIN_RX, PIN_TX);

    // Restart takes quite some time
    // To skip it, call init() instead of restart()
    Serial.println("Initializing modem...");
    if (!modem.restart()) {
        Serial.println("Failed to restart modem, attempting to continue without restarting");
    }



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

#if TINY_GSM_USE_GPRS && defined TINY_GSM_MODEM_XBEE
    // The XBee must run the gprsConnect function BEFORE waiting for network!
    modem.gprsConnect(apn, gprsUser, gprsPass);
#endif

    SerialMon.print("Waiting for network...");
    if (!modem.waitForNetwork()) {
        SerialMon.println(" fail");
        delay(10000);
        return;
    }
    SerialMon.println(" success");

    if (modem.isNetworkConnected()) {
        SerialMon.println("Network connected");
    }

#if TINY_GSM_USE_GPRS
    // GPRS connection parameters are usually set after network registration
    SerialMon.print(F("Connecting to "));
    SerialMon.print(apn);
    if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
        SerialMon.println(" fail");
        delay(10000);
        return;
    }
    SerialMon.println(" success");

    if (modem.isGprsConnected()) {
        SerialMon.println("GPRS connected");
    }
#endif

    // MQTT Broker setup
    mqtt.setServer(broker, 1883);
    mqtt.setCallback(mqttCallback);

}


void loop()
{


    // Make sure we're still registered on the network
    if (!modem.isNetworkConnected()) {
        SerialMon.println("Network disconnected");
        if (!modem.waitForNetwork(180000L, true)) {
            SerialMon.println(" fail");
            delay(10000);
            return;
        }
        if (modem.isNetworkConnected()) {
            SerialMon.println("Network re-connected");
        }

#if TINY_GSM_USE_GPRS
        // and make sure GPRS/EPS is still connected
        if (!modem.isGprsConnected()) {
            SerialMon.println("GPRS disconnected!");
            SerialMon.print(F("Connecting to "));
            SerialMon.print(apn);
            if (!modem.gprsConnect(apn, gprsUser, gprsPass)) {
                SerialMon.println(" fail");
                delay(10000);
                return;
            }
            if (modem.isGprsConnected()) {
                SerialMon.println("GPRS reconnected");
            }
        }
#endif
    }

    if (!mqtt.connected()) {
        SerialMon.println("=== MQTT NOT CONNECTED ===");
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


