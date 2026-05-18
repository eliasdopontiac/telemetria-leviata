# 📡 LilyGO T-SIM7000G LTE Gateway

Este firmware transforma a placa LilyGO em um Gateway IoT para a embarcação Leviatã. Ele opera como a "Ponte para a Nuvem", conectando o barco à rede celular 4G/LTE.

## 🛠️ O que este firmware faz?

1. **Recepção ESP-NOW (Alta Velocidade):** Escuta passivamente a rede local do barco para capturar os pacotes binários compactados (`struct_telemetry`) enviados pelo Hub Central (Heltec V3).
2. **Monitoramento Interno:** Lê a voltagem da própria bateria de lítio da placa via pino ADC (`BAT_ADC 35`), garantindo que o envio de dados não pare por falta de energia (`v_sist`).
3. **Tradução de Protocolo:** Desempacota o binário e reconstrói o formato JSON aninhado completo.
4. **Envio MQTT (LTE):** Publica o JSON na nuvem usando o modem SIM7000G através da rede da Claro.

## ⚙️ Configuração do Hardware

- **Cartão SIM:** Inserir um nano-SIM ativo. As credenciais (APN, User, Pass) estão configuradas para a `claro.com.br` no código fonte.
- **Bateria:** É fortemente recomendado o uso de uma bateria Li-ion/LiPo conectada ao conector JST da placa para suprir os picos de 2A do modem LTE.
- **MAC Address:** Para que a Heltec consiga enviar os dados via ESP-NOW, você precisa descobrir o MAC Address desta placa. O firmware imprime o MAC Address na porta Serial (115200 baud) logo que liga.

## 📊 Estrutura de Envio (MQTT)

O Gateway posta no tópico `leviata/telemetria/race` o seguinte formato:

```json
{
  "solar": {"tensao": 46.5, "corrente": 5.9, "pot": 277},
  "bateria": {"soc": 0, "tensao_bat": 50.7, "corrente_liq": -10.6},
  "prop": {"rpm": 1314, "i_motor": 16.6, "t_motor": 54, "t_ctrl": 37, "fardriver_falha": 0},
  "nav": {"vel": 19.7, "lat": -3.1194, "lon": -60.0216, "gps_satelites": 10, "gps_hora": "12:00:00", "proa": 184.8, "hdop": 0.8},
  "sinal": {"lora_pacotes": 0, "lora": 0, "lte": 25},
  "v_sist": 4.0
}
```
