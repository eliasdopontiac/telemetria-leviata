# 🚤 Telemetria Leviatã v2026

![Flet](https://img.shields.io/badge/UI-Flet-blue?style=for-the-badge&logo=python)
![MQTT](https://img.shields.io/badge/Link-MQTT-green?style=for-the-badge&logo=mqtt)
![LoRa](https://img.shields.io/badge/Radio-LoRa-purple?style=for-the-badge)

Sistema de telemetria redundante desenvolvido para o monitoramento em tempo real do barco solar da equipe **Leviatã**. A aplicação processa dados via rádio (LoRa/Serial) e internet (LTE/LilyGO), oferecendo análises críticas para estratégia de prova e segurança do hardware.

## 📊 Funcionalidades Principais

- **Monitoramento em Tempo Real (Aba Telemetria):**
    - **Velocidade Dual:** Mostrador gigante em Km/h com conversão instantânea para Nós (kt).
    - **Gestão de Energia:** Nível de bateria (SoC %), Tensão do banco e Corrente Líquida (Balanço Carga/Descarga).
    - **Estimativa de Autonomia:** Cálculo preditivo de tempo restante e distância (km) com base no consumo atual.
    - **Segurança Térmica:** Alertas visuais por cores para temperaturas do Motor e Controladora.
    - **Navegação:** Mapa interativo com GPS e função de Auto-centro.

- **Análise de Desempenho (Aba Análise):**
    - 4 Gráficos históricos sincronizados (Velocidade, Potência Solar, Corrente Motor e Corrente Bateria).
    - Memória de até 200 pontos para visualização de tendências.

- **Diagnóstico de Rede:**
    - Indicadores de qualidade de sinal para LTE (CSQ) e LoRa (RSSI).
    - Contador de *Packet Loss* (Perda de Pacotes) em tempo real.

## 🛠️ Requisitos do Sistema

- **Python 3.10+**
- **Bibliotecas Python:** `flet`, `pyserial`, `paho-mqtt`, `flet-charts`, `flet-map`.
- **Hardware Transmissor:** ESP32 ou LilyGO T-SIM7000G configurado conforme o arquivo `.ino` incluso.

## 🚀 Como Executar

1. **Clone o repositório e acesse a pasta:**
   ```powershell
   git clone https://github.com/telemetria-leviata/Telemetria_2026.git
   cd "estação base"
   ```

2. **Instale as dependências:**
   ```powershell
   pip install flet pyserial paho-mqtt flet-charts flet-map
   ```

3. **Inicie a Estação Base:**
   ```powershell
   python main.py
   ```

## 📦 Gerando o Executável (.exe)

Para rodar em computadores sem Python instalado, utilize o PyInstaller com o comando de coleta de recursos do Flet:

```powershell
python -m PyInstaller --noconsole --onefile --collect-all flet --collect-all flet_charts --collect-all flet_map --name "Telemetria_Leviata_2026" main.py
```

## 📡 Protocolo de Dados (JSON)

A Estação Base espera um objeto JSON via Serial ou MQTT no seguinte formato:

```json
{
  "solar": {"tensao": 48.2, "corrente": 5.0, "pot": 241},
  "bateria": {"soc": 98.5, "tensao_bat": 53.1, "corrente_liq": -3.5},
  "prop": {"rpm": 1500, "i_motor": 8.5, "t_motor": 45, "t_ctrl": 38, "fardriver_falha": 0},
  "nav": {"vel": 15.5, "lat": -3.11902, "lon": -60.02173, "gps_hora": "12:00:00", "gps_satelites": 10},
  "sinal": {"lora": -80, "lte": 22, "lora_pacotes": 1240}
}
```

## 🔧 Configurações (`config.py`)

Você pode ajustar parâmetros como capacidade da bateria e tópicos MQTT no arquivo de configuração:
- `BAT_CAPACITY_AH`: Capacidade nominal (ex: 40.0 para 40Ah).
- `MQTT_BROKER`: Endereço do servidor (padrão: `broker.hivemq.com`).
- `POT_MAX`: Limite da escala de potência solar no dashboard.

---
Desenvolvido por Gemini para Equipe Leviatã 2026.
