# 🚤 Telemetria Leviatã v2026 (Modo Competição)

![Flet](https://img.shields.io/badge/UI-Flet-blue?style=for-the-badge&logo=python)
![MQTT](https://img.shields.io/badge/Link-MQTT-green?style=for-the-badge&logo=mqtt)
![LoRa](https://img.shields.io/badge/Radio-LoRa-purple?style=for-the-badge)

Sistema de telemetria de **Alta Resolução (2.5s)** desenvolvido para o monitoramento em tempo real do barco solar da equipe **Leviatã**. A aplicação processa dados via rádio (LoRa via cabo USB) e internet (LTE/MQTT via Nuvem), oferecendo análises críticas para estratégia de prova.

## 📊 Funcionalidades Principais

- **Monitoramento Tático em Tempo Real:**
    - **Navegação:** Mapa interativo, Velocidade (Km/h e Nós), Satélites, **Proa (Heading)** e **Precisão (HDOP)**.
    - **Gestão de Energia:** Nível de bateria (SoC %), Tensão do banco, Corrente Líquida (Balanço Carga/Descarga) e Tensão do Sistema Emissor (`v_sist`).
    - **Estimativa de Autonomia:** Cálculo preditivo de tempo restante e distância com base no consumo atual.
    - **Segurança da Propulsão:** Leitura dos 15 códigos de falha originais da **Fardriver** e Alertas visuais por cores para temperaturas.

- **Análise de Desempenho (Aba Análise):**
    - 4 Gráficos históricos sincronizados (Velocidade, Potência Solar, Corrente Motor e Corrente Bateria).
    - Memória de até 200 pontos dinâmicos.

- **Diagnóstico de Rede:**
    - Indicadores de qualidade de sinal para LTE (CSQ) e LoRa (RSSI).
    - Monitoramento de bateria das placas de transmissão (LilyGO/Heltec).

## 🛠️ Requisitos do Sistema

- **Python 3.10+**
- **Bibliotecas Python:** `flet`, `pyserial`, `paho-mqtt`, `flet-charts`, `flet-map`.
- Placa receptora LoRa conectada via USB (Heltec V3 rodando o firmware `LoRa Base`).

## 🚀 Como Executar

1. **Instale as dependências:**
   ```powershell
   pip install flet pyserial paho-mqtt flet-charts flet-map
   ```

2. **Inicie a Estação Base:**
   ```powershell
   python main.py
   ```

## 📦 Gerando o Executável (.exe)

Para rodar em computadores da equipe sem Python, compile usando o PyInstaller:

```powershell
python -m PyInstaller --noconsole --onefile --collect-all flet --collect-all flet_charts --collect-all flet_map --name "Telemetria_Leviata_2026" main.py
```

## 📡 Protocolo de Dados (JSON Unificado)

A Estação Base espera um objeto JSON (seja pela porta USB do LoRa ou pelo broker MQTT) no exato formato abaixo:

```json
{
  "solar": {"tensao": 46.5, "corrente": 5.9, "pot": 277},
  "bateria": {"soc": 0, "tensao_bat": 50.7, "corrente_liq": -10.6},
  "prop": {"rpm": 1314, "i_motor": 16.6, "t_motor": 54, "t_ctrl": 37, "fardriver_falha": 0},
  "nav": {"vel": 19.7, "lat": -3.1194, "lon": -60.0216, "gps_satelites": 10, "gps_hora": "12:00:00", "proa": 184.8, "hdop": 0.8},
  "sinal": {"lora_pacotes": 125, "lora": -83, "lte": 29},
  "v_sist": 4.1
}
```

## 📂 Estrutura do Backend
O arquivo `backend.py` consolida as informações deste JSON e grava cada pacote recebido no arquivo `telemetria_solar.csv`, garantindo que o log da prova seja salvo permanentemente.

---
**Engenharia de Software:** Arquitetura Dual-Radio (ESP-NOW + LTE / LoRa) e Protocolos Fardriver Pro/VE.Direct implementados para Equipe Leviatã.
