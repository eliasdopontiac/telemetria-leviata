//Bibliotecas declaradas
#define BLYNK_PRINT Serial

#define BLYNK_TEMPLATE_ID "TMPL2aZk7As5Q"
#define BLYNK_TEMPLATE_NAME "LED ESP32"
#define BLYNK_AUTH_TOKEN "yBDQLnwKa-CaRDH5qBq9R5IjuckEbLJ-"

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>

//#include <IRremoteESP8266.h>
#include <IRsend.h>



char ssid[] = "TIM WIFI_2G";
char pass[] = "lesamy2106";

IRsend irsend1(12); //led emissor IR conectado ao pino (D5)
uint16_t tamanho1 = 255; //TAMANHO DA LINHA RAW(100 BLOCOS)
uint16_t frequencia1 = 32; //FREQUÊNCIA DO SINAL IR(32KHz)
uint16_t raw1Data[] = { 4371, -4384, 717, -500, 710, -499, 710, -1499, 709, -500, 691, -519, 683, -1524, 685, -526, 684, -500, 710, -499, 684, -1523, 684, -1524, 685, -528, 680, -530, 680, -1529, 679, -531, 677, -1508, 701, -535, 676, -533, 650, -559, 650, -560, 650, -534, 676, -534, 675, -1532, 676, -534, 651, -558, 650, -560, 650, -533, 675, -534, 676, -534, 650, -560, 650, -559, 650, -533, 677, -534, 676, -534, 676, -534, 650, -559, 651, -536, 675, -1533, 677, -532, 677, -534, 650, -1559, 650, -560, 650, -559, 650, -534, 676, -534, 675, -534, 651, -559, 651, -560, 648, -1560, 650, -533, 675, -539, 671, -1534, 675, -535, 649, -560, 650, -1559, 649, -560, 650, -40144, 9038, -4531, 651, -586, 624, -587, 623, -586, 624, -1690, 650, -560, 649, -1690, 625, -587, 623, -1691, 624, -586, 625, -1691, 650, -1663, 650, -586, 624, -586, 623, -586, 625, -586, 650, -560, 652, -584, 623, -585, 624, -587, 624, -587, 623, -586, 650, -1665, 650, -1691, 623, -587, 623, -587, 624, -586, 623, -587, 649, -587, 623, -1691, 626, -584, 622, -1699, 616, -586, 623, -586, 650, -1691, 622, -587, 623, -20102, 624, -585, 625, -588, 647, -561, 649, -586, 624, -586, 624, -586, 624, -586, 623, -587, 649, -1692, 623, -586, 624, -586, 623, -587, 621, -589, 649, -561, 649, -587, 623, -587, 623, -587, 623, -587, 648, -561, 650, -589, 620, -588, 621, -588, 622, -587, 623, -588, 649, -561, 650, -587, 622, -588, 622, -588, 623, -587, 622, -588, 648, -587, 622, -1692, 622, };
//
//IRsend irsend2(4); //led emissor IR conectado ao pino (D5)
//uint16_t tamanho2 = 197; //TAMANHO DA LINHA RAW(100 BLOCOS)
//uint16_t frequencia2 = 38; //FREQUÊNCIA DO SINAL IR(32KHz)
//uint16_t raw2Data[] = { 6116, 7372, 572, 1624, 560, 1628, 568, 1624, 564, 1628, 568, 1648, 536, 1684, 512, 1652, 556, 1636, 560, 560, 564, 580, 544, 576, 560, 560, 564, 580, 544, 576, 560, 560, 564, 580, 544, 1644, 540, 1652, 568, 1620, 564, 1628, 568, 1624, 564, 1652, 532, 1656, 560, 1632, 564, 556, 560, 584, 540, 580, 564, 556, 560, 584, 540, 576, 568, 552, 564, 580, 544, 1644, 560, 1632, 564, 1624, 564, 1624, 572, 1644, 564, 1628, 568, 1620, 564, 1628, 556, 588, 540, 576, 568, 552, 560, 584, 540, 580, 568, 576, 536, 584, 564, 552, 572, 1616, 568, 1648, 540, 1648, 568, 552, 560, 584, 540, 580, 568, 548, 564, 1624, 564, 580, 564, 556, 568, 576, 540, 1648, 568, 1620, 564, 1624, 564, 1656, 528, 584, 560, 1628, 568, 576, 540, 580, 564, 1624, 564, 1624, 560, 584, 560, 1628, 572, 1616, 568, 576, 536, 1652, 568, 1620, 564, 580, 536, 584, 560, 1628, 568, 576, 536, 580, 568, 552, 560, 1652, 536, 584, 560, 1624, 560, 584, 564, 1624, 560, 560, 564, 580, 556, 1628, 568, 552, 564, 1648, 536, 584, 560, 1628, 560, 580, 564, 1624, 560, 1628, 572, 7380, 560 };
//
//I5
//uint16_t tamanho3 = 199; //TAMANHO DA LINHA RAW(100 BLOCOS)
//uint16_t frequencia3 = 38; //FREQUÊNCIA DO SINAL IR(32KHz)
//uint16_t raw3Data[] = { 4428, 4360, 564, 1620, 564, 556, 544, 1644, 540, 1644, 540, 556, 536, 560, 536, 1620, 560, 564, 540, 556, 536, 1624, 572, 552, 540, 556, 536, 1648, 536, 1644, 540, 556, 544, 1620, 564, 1652, 544, 552, 540, 1624, 572, 1636, 548, 1608, 564, 1620, 564, 1620, 564, 1624, 568, 556, 540, 1616, 564, 560, 544, 552, 540, 556, 536, 560, 544, 552, 540, 556, 536, 560, 540, 1644, 540, 556, 536, 560, 544, 552, 540, 556, 536, 560, 544, 552, 540, 1648, 544, 552, 540, 1624, 560, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 5232, 4428, 4368, 568, 1616, 568, 552, 540, 1624, 568, 1616, 568, 552, 540, 556, 536, 1620, 564, 560, 544, 556, 536, 1624, 572, 552, 540, 556, 536, 1644, 540, 1620, 564, 556, 544, 1620, 564, 1624, 572, 552, 540, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 560, 544, 1616, 568, 552, 540, 556, 544, 552, 540, 556, 536, 560, 544, 552, 540, 560, 544, 1636, 544, 556, 536, 556, 536, 560, 544, 552, 540, 556, 536, 560, 544, 1648, 536, 560, 540, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1624, 560 };
//
//IRsend irsend4(4); //led emissor IR conectado ao pino (D5)
//uint16_t tamanho4 = 199; //TAMANHO DA LINHA RAW(100 BLOCOS)
//uint16_t frequencia4 = 38; //FREQUÊNCIA DO SINAL IR(32KHz)
//uint16_t raw4Data[] = { 4428, 4384, 564, 1620, 564, 556, 544, 1620, 564, 1620, 564, 556, 536, 560, 544, 1616, 568, 556, 536, 560, 540, 1624, 560, 560, 544, 552, 540, 1620, 564, 1620, 564, 556, 548, 1616, 568, 556, 544, 1616, 568, 1616, 568, 1616, 568, 1616, 568, 552, 540, 1624, 560, 1624, 572, 1620, 568, 556, 544, 552, 540, 556, 536, 560, 540, 1616, 568, 556, 536, 560, 544, 1620, 564, 1620, 564, 1620, 564, 560, 540, 556, 536, 560, 544, 552, 540, 556, 548, 552, 540, 556, 536, 560, 540, 1620, 564, 1620, 564, 1620, 564, 1624, 560, 1624, 564, 5232, 4424, 4376, 572, 1612, 572, 552, 540, 1620, 572, 1612, 572, 552, 544, 552, 536, 1620, 564, 560, 544, 556, 548, 1616, 564, 556, 536, 560, 544, 1616, 568, 1616, 568, 552, 540, 1628, 568, 556, 536, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 560, 540, 1620, 564, 1624, 560, 1628, 568, 556, 536, 560, 544, 552, 540, 556, 544, 1616, 568, 552, 540, 560, 544, 1620, 564, 1620, 564, 1620, 564, 556, 548, 548, 540, 560, 532, 564, 540, 556, 536, 560, 544, 552, 540, 560, 540, 1620, 564, 1620, 564, 1620, 564, 1620, 564, 1624, 572 };
//
//IRsend irsend5(4); //led emissor IR conectado ao pino (D5)
//uint16_t tamanho5 = 211; //TAMANHO DA LINHA RAW(100 BLOCOS)
//uint16_t frequencia5 = 38; //FREQUÊNCIA DO SINAL IR(32KHz)
//uint16_t raw5Data[] = { 9020, 4476, 576, 1668, 576, 1672, 568, 568, 544, 564, 548, 536, 568, 568, 544, 1672, 576, 1696, 540, 1680, 568, 1676, 572, 1672, 576, 560, 544, 1676, 572, 1672, 576, 1668, 576, 560, 544, 568, 544, 564, 540, 568, 544, 564, 552, 560, 540, 1676, 572, 1700, 548, 1672, 564, 544, 572, 564, 548, 560, 544, 568, 544, 564, 540, 568, 544, 564, 548, 564, 540, 568, 548, 560, 540, 568, 548, 564, 548, 560, 540, 1676, 572, 564, 552, 560, 540, 568, 548, 560, 540, 568, 548, 564, 548, 560, 544, 564, 548, 1696, 552, 560, 544, 564, 548, 560, 544, 568, 544, 564, 548, 560, 544, 1700, 548, 536, 576, 532, 572, 564, 548, 560, 544, 568, 544, 564, 548, 560, 544, 564, 548, 564, 540, 568, 548, 560, 552, 560, 540, 568, 548, 560, 540, 568, 548, 536, 564, 572, 544, 564, 548, 560, 544, 564, 548, 564, 540, 568, 544, 564, 548, 1696, 544, 568, 544, 564, 548, 560, 544, 564, 548, 564, 540, 568, 544, 564, 548, 564, 540, 568, 544, 536, 568, 1680, 568, 564, 548, 1672, 576, 560, 544, 564, 548, 564, 540, 568, 544, 564, 548, 1696, 544, 1676, 572, 1672, 576, 1668, 576, 1672, 568, 1676, 568, 568, 548, 1668, 568 };
//
//IRsend irsend6(4); //led emissor IR conectado ao pino (D5)
//uint16_t tamanho6 = 213; //TAMANHO DA LINHA RAW(100 BLOCOS)
//uint16_t frequencia6 = 38; //FREQUÊNCIA DO SINAL IR(32KHz)
//uint16_t raw6Data[] = { 9020, 4476, 576, 1668, 572, 1676, 568, 568, 548, 560, 544, 564, 548, 564, 548, 1668, 572, 1676, 568, 1676, 572, 1672, 576, 1668, 568, 568, 548, 1672, 576, 1668, 580, 1668, 568, 568, 544, 564, 548, 560, 544, 564, 548, 564, 540, 568, 548, 1668, 576, 1672, 568, 1676, 572, 564, 548, 560, 544, 568, 544, 564, 548, 560, 544, 568, 544, 564, 540, 568, 544, 564, 552, 560, 544, 564, 548, 560, 540, 568, 548, 1672, 576, 560, 540, 568, 548, 560, 552, 560, 544, 564, 548, 560, 544, 564, 548, 564, 540, 1676, 572, 564, 548, 560, 544, 568, 544, 564, 548, 560, 544, 564, 548, 1672, 576, 560, 544, 564, 548, 560, 544, 568, 544, 564, 540, 568, 544, 564, 552, 560, 540, 568, 548, 560, 540, 568, 548, 564, 548, 560, 544, 564, 548, 560, 544, 568, 544, 564, 552, 556, 544, 568, 548, 560, 540, 568, 548, 560, 540, 572, 544, 564, 548, 560, 544, 564, 548, 560, 544, 568, 544, 564, 548, 560, 544, 564, 548, 564, 540, 568, 544, 564, 552, 1668, 568, 568, 544, 1672, 576, 560, 544, 564, 548, 564, 540, 568, 544, 564, 552, 1668, 568, 1676, 572, 1672, 576, 1668, 580, 1668, 568, 568, 544, 564, 548, 1668, 572, 42368, 176 };

BLYNK_WRITE(V1){
 int onoff = param.asInt();
 if(onoff == 1){
 irsend1.sendRaw(raw1Data,tamanho1,frequencia1);
}
}
//BLYNK_WRITE(V2){
// int onoff = param.asInt();
// if(onoff == 1){
// irsend2.sendRaw(raw2Data,tamanho2,frequencia2);
//}
//}
//BLYNK_WRITE(V3){
// int onoff = param.asInt();
// if(onoff == 1){
// irsend3.sendRaw(raw3Data,tamanho3,frequencia3);
//}
//}
//BLYNK_WRITE(V4){
// int onoff = param.asInt();
// if(onoff == 1){
// irsend4.sendRaw(raw4Data,tamanho4,frequencia4);
//}
//}
//BLYNK_WRITE(V5){
// int onoff = param.asInt();
// if(onoff == 1){
// irsend5.sendRaw(raw5Data,tamanho5,frequencia5);
//}
//}
//BLYNK_WRITE(V6){
// int onoff = param.asInt();
// if(onoff == 1){
// irsend6.sendRaw(raw6Data,tamanho6,frequencia6);
//}
//}
//BLYNK_WRITE(V7){
// int onoff = param.asInt();
// pinMode(5,OUTPUT);
// if(onoff == 1){
// digitalWrite(5,HIGH);
// delay(500);
// digitalWrite(5,LOW);
//}
//}
BLYNK_WRITE(V0){
 int onoff = param.asInt();
 pinMode(27,OUTPUT);
 if(onoff == 1){
 digitalWrite(27,HIGH);}
else{ digitalWrite(27,LOW);
}
}
void setup()
{
 irsend1.begin();
// irsend2.begin();
// irsend3.begin();
// irsend4.begin();
// irsend5.begin();
// irsend6.begin();
Serial.begin(9600);
pinMode(12,OUTPUT);
 Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}
BLYNK_CONNECTED(){
 Blynk.syncVirtual(V1);
// Blynk.syncVirtual(V2);
// Blynk.syncVirtual(V3);
// Blynk.syncVirtual(V4);
// Blynk.syncVirtual(V5);
// Blynk.syncVirtual(V6);
// Blynk.syncVirtual(V7);
 Blynk.syncVirtual(V0);
}



void loop() {
 Blynk.run();
}
