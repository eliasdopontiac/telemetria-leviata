# 🚤 Equipe Leviatã 2026 - Estação Base Web de Telemetria

Sistema moderno de monitoramento em tempo real da telemetria do barco solar da **Equipe Leviatã (UEA)**. Desenvolvido para operação de pista com suporte a conexão Serial USB (ESP32 / LoRa Base), armazenamento local SQLite, transmissão multi-dispositivo via Wi-Fi (Socket.IO) e executável portátil de 1 clique.

---

## ⚡ Recursos Principais

- **Dashboard Futurista & Responsivo**:
  - **Manômetros Circulares Neumórficos**: Velocidade (km/h), RPM e Potência Solar (W).
  - **Status da Bateria LiFePO4**: Indicador de Carga (SOC %), Tensão em Volts (51.2V), Autonomia Estimada (h) e Saldo de Potência (W).
  - **Mapa da Raia da Prova (GPS)**: Rastreamento em tempo real com Leaflet (OpenStreetMap), marcador em laranja neon do barco com orientação de proa (°), contagem de satélites e registro do trajeto.
  - **Métricas Críticas & Alertas (Fardriver)**: Temperatura do Motor, Temperatura da Caixa Eletrônica (Controlador), Corrente de Consumo e **Histórico de Falhas Fardriver** com registro de eventos e carimbo de data/hora.
  - **Gráfico de Energia em Tempo Real**: Curvas de Entrada Solar (A) vs. Saída Motor (A) atualizados dinamicamente.
  - **Cronômetro do Pit Wall**: Marcação manual de voltas, melhor volta (*Best Lap*) e velocidade média.
- **Portabilidade 100% Autônoma (Sem instalação)**:
  - Inclui Node.js portátil embutido. Basta 2 cliques para rodar em qualquer notebook Windows na pista sem instalar nada.
- **Transmissão Multi-Dispositivo (Wi-Fi)**:
  - Transmite os dados instantaneamente para celulares, tablets e outros notebooks conectados à mesma rede da base.

---

## 🚀 Como Rodar na Pista (1 Clique)

### 🎒 Modo Portátil (Qualquer Notebook Windows)
1. Copie a pasta **`estação base web`** para o notebook ou pendrive.
2. Dê **2 cliques** no arquivo:
   ```cmd
   START_TELEMETRIA.bat
   ```
3. O servidor será iniciado e o navegador abrirá **automaticamente** no painel central:
   👉 `http://localhost:3001`

### 📱 Acesso de Outros Dispositivos na Rede
Qualquer membro da equipe conectado no Wi-Fi da base pode abrir o painel pelo celular ou tablet acessando o IP do computador na porta `:3001`:
👉 `http://<IP_DO_NOTEBOOK_BASE>:3001`

---

## 🛠️ Desenvolvedores / Modo de Desenvolvimento

Se quiser editar o código-fonte em tempo de desenvolvimento:

### 1. Iniciar o Backend Node.js
```bash
cd "backend-node"
npm install
node server.js
```

### 2. Iniciar o Frontend React (Vite Hot Reload)
```bash
cd "frontend-react"
npm install
npm run dev
```
Acesse `http://localhost:5173`.

---

## 🛰️ Protocolo Serial JSON (ESP32 / LoRa Base)

A estação base aguarda um payload JSON enviado via Serial (115200 bps) a cada 1 segundo no seguinte formato:

```json
{
  "solar": {
    "tensao": 46.5,
    "corrente": 6.8,
    "pot": 316.2
  },
  "bateria": {
    "soc": 88.5,
    "tensao_bat": 51.2,
    "corrente_liq": -12.4
  },
  "prop": {
    "rpm": 1450,
    "i_motor": 19.2,
    "t_motor": 48.5,
    "t_ctrl": 36.2,
    "fardriver_falha": 0
  },
  "nav": {
    "vel": 21.8,
    "lat": -3.119020,
    "lon": -60.021730,
    "gps_satelites": 12,
    "gps_hora": "15:30:45",
    "proa": 175.4,
    "hdop": 0.95
  },
  "sinal": {
    "lora_pacotes": 1420,
    "lora": -78,
    "lte": 22
  },
  "v_sist": 4.10
}
```

### 💻 Simulador ESP32
Para testar a estação base sem a rádio LoRa física conectada, grave o código `simulador_esp32_serial.ino` em uma placa ESP32. Ela simulará as variações reais do barco navegando na raia de prova em Manaus.

---

## 📂 Estrutura do Projeto

```text
estação base web/
├── START_TELEMETRIA.bat       # Lançador de 1 clique para pista
├── node/                      # Node.js portátil (Windows)
├── backend-node/              # Servidor Node.js, Serial, SQLite3 e Socket.IO
│   ├── server.js              # Ponto de entrada do servidor API/WebSocket
│   ├── serialManager.js       # Gerenciador da porta Serial USB (115200 bps)
│   ├── database.js            # Conexão SQLite (telemetria.db)
│   └── telemetria.db          # Banco de dados SQLite local
└── frontend-react/            # Interface React 19 + Vite
    ├── dist/                  # Build de produção servido pelo Express
    ├── src/
    │   ├── assets/            # Animações Lottie e ícones
    │   ├── components/        # Manômetros, Mapa, Histórico de Falhas, Bateria, Logo
    │   ├── pages/             # DashboardPage e AnalyticsPage
    │   └── index.css          # Design System Neumórfico Dark Mode
    └── package.json
```

---

## 🏆 Equipe Leviatã 2026 - Universidade do Estado do Amazonas (UEA)
*Desenvolvido para máxima confiabilidade, performance e facilidade de operação durante as competições de barcos solares.*
