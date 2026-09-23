# 📡 Estação Base — Sistema de Telemetria Leviatã 2026

Este diretório contém **duas gerações** do sistema de telemetria da estação base em terra.

---

## 🌐 Versão Web — Node.js + React (PRODUÇÃO ATUAL)

Localização: [`estação base web/`](estação%20base%20web/)

O sistema de produção atual para uso em pista. Interface web acessível de qualquer dispositivo na rede local.

### Como usar
1. Abra a pasta `estação base web/`
2. Duplo-clique em **`START_TELEMETRIA.bat`**
3. O painel abrirá em `http://localhost:3001`

### Portabilidade
O arquivo **`estação base web.zip`** contém a versão portátil completa com Node.js embutido — basta extrair e executar o `.bat` em qualquer notebook sem precisar de instalações.

### Arquitetura
```
[Rádio LoRa ESP32] ──USB── [backend-node/server.js]
                                    │
                             SQLite (telemetria.db)
                                    │
                             Socket.IO (WebSocket)
                                    │
                         [frontend-react/ Dashboard]
```

### Conexão com o barco
- **Serial Server** (recomendado para pista): Backend lê a USB e salva no banco de dados.
- **USB Direto / Web Serial**: Browser lê a USB diretamente, sem salvar no banco.

---

## 🐍 Versão Python — CustomTkinter (LEGADO)

Localização: Arquivos `.py` na raiz desta pasta (`dashboard.py`, `backend.py`, etc.)

Versão anterior do sistema, desenvolvida com CustomTkinter (Python). Mantida como referência histórica e fallback de emergência.

---

## 📟 Firmware da Estação Base LoRa

Localização: [`LoRa Base/Firmware_Base_LoRa.ino`](LoRa%20Base/)

Código C++ para o ESP32 que fica na tenda da equipe recebendo os pacotes LoRa do barco e retransmitindo via USB Serial para o backend Node.js.

---

## 🔧 Simulador (Desenvolvimento)

Localização: [`estação base web/simulador_esp32_serial.ino`](estação%20base%20web/simulador_esp32_serial.ino)

Carregue este código em qualquer ESP32 para simular os pacotes LoRa do barco durante testes de mesa. Gera dados de telemetria realistas a 1Hz.

**Comandos de teste via Serial Monitor:**
- `FAULT:4` → Simula superaquecimento do motor (>85°C)
- `FAULT:1` → Simula sobretensão na bateria
- `CLEAR` → Limpa todas as falhas simuladas
