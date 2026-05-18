# 🧠 Hub Central Heltec V3 (Sender)

Este firmware transforma a **Heltec WiFi LoRa 32 V3** no "Cérebro" de aquisição de dados do barco. Ele foi projetado para **Telemetria de Alta Resolução (Modo Competição)**, atualizando as métricas a cada **2.5 segundos** (0.4 Hz).

## 🛠️ Aquisição de Sensores (Matrizes)

O Hub lê 3 fontes de dados simultaneamente utilizando as 3 portas Seriais físicas (UART) do chip ESP32-S3:

1. **Fardriver Pro (Serial2 - RX41/TX42):** Executa comunicação bidirecional. Envia pacotes `Keep-Alive`, calcula CRC16 e decodifica pacotes de Voltagem, Corrente, RPM, Temperaturas e **15 Códigos de Erro**.
2. **GPS (Serial1 - RX7/TX6):** Captura Latitude, Longitude, Velocidade, Proa (Heading), Precisão (HDOP), Satélites e a **Hora Atômica** (Relógio Mestre).
3. **Victron MPPT (Serial0 - RX39/TX38):** Lê o protocolo VE.Direct para capturar Voltagem, Corrente e Potência (Watts) gerada pelos painéis solares em tempo real.

## 📡 Transmissão Dual-Radio

- **LoRa (Para Terra):** Para não estourar o tempo de antena, todos os dados são comprimidos em uma `struct __attribute__((packed))` de ~40 bytes. Transmitido via rádio SX1262 em 915MHz com Spreading Factor 10 (Alcance e velocidade ideais para competição).
- **ESP-NOW (Para a Nuvem):** Envia uma cópia exata do binário para a placa LilyGO dentro do barco, que atua como gateway LTE.

## ⚠️ Notas de Hardware (Heltec V3)

- Diferente da V2, a Heltec V3 requer que o pino `VEXT_PIN (36)` seja acionado em `LOW` no `setup()` para energizar o display OLED e os sensores externos.
- O chip LoRa é o SX1262, utilizando os pinos SPI: NSS(8), SCK(9), MOSI(10), MISO(11), RST(12) e DIO1(14).
