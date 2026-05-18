# 📡 Estação Base LoRa (Receptor)

Este firmware foi desenvolvido para a placa **Heltec WiFi LoRa 32 V3** que ficará em terra com a equipe, conectada via cabo USB ao computador.

## 🛠️ O que este firmware faz?

1. **Recepção LoRa (SF10 / 915MHz):** Escuta ativamente a frequência procurando os pacotes de 40 bytes emitidos pelo barco a cada 2.5 segundos.
2. **Validação de Integridade:** Checa o `sync_byte (0xAA)` para garantir que o pacote não sofreu corrupção de rádio (ruído) antes de processá-lo.
3. **Reconstrução (Binário -> JSON):** Desempacota a estrutura C++ ultraleve (que contém RPM, HDOP, Proa, Correntes, Temperaturas, etc).
4. **Alimentação do Dashboard:** Cria um JSON aninhado idêntico àquele que a LilyGO cria na nuvem. Imprime este JSON diretamente na porta Serial (USB). 

## 💻 Integração com Python

O aplicativo `backend.py` rodando no seu notebook escuta a porta COM desta placa. Ao ler a linha com o JSON, o Python grava os dados no arquivo `telemetria_solar.csv` e atualiza a interface gráfica do Flet em tempo real.

Nenhum processamento pesado é feito no computador; a placa Heltec já entrega os dados formatados e mastigados.

## 📺 Feedback Local (OLED)

A placa possui um painel OLED de diagnóstico rápido. Se o notebook travar ou acabar a bateria, você pode olhar para a telinha da placa para ver:
- Quantos pacotes foram recebidos.
- Nível do Sinal (RSSI e SNR).
- RPM, Consumo (A) e Velocidade do Barco (km/h) instantâneos.
