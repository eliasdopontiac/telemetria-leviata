# 🚤 Equipe Leviatã 2026 - Estação Base Web de Telemetria

Sistema moderno e resiliente de monitoramento em tempo real da telemetria do barco solar da **Equipe Leviatã (Universidade do Estado do Amazonas - UEA)** para o **Desafio Solar Brasil**.

Desenvolvido para operação de pista com suporte a conexão Serial USB (ESP32 / LoRa Base), banco de dados local SQLite3 com deduplicação, transmissão multi-dispositivo via Wi-Fi (Socket.IO), sincronização online tolerante a falhas entre estações e executáveis portáteis de 1 clique.

---

## 🎬 Preview

### Visão Geral — Dashboard em Tempo Real
![Dashboard Visão Geral](animacao.gif)

### Gráficos de Telemetria e Eficiência
![Gráficos de Telemetria](grafico.gif)

---

## ⚡ Recursos Principais

- **Dashboard de Engenharia em Tempo Real**:
  - **Manômetros Circulares Neumórficos**: Velocidade náutica (km/h e nós), RPM e Potência dos painéis solares (W).
  - **Status do Banco de Baterias (LiFePO4)**: Carga Útil (SOC %), Tensão (51.2V nominais), Corrente Líquida (A), Autonomia Estimada (h) e Saldo Energético (Geração vs Consumo).
  - **Rastreamento GPS da Raia**: Mapa interativo com Leaflet na **Lagoa de Imboassica (Macaé - RJ)** (`-22.4154835, -41.8178226`), marcador em laranja neon com orientação dinâmica da proa (°), contagem de satélites e rastro de navegação.
  - **Métricas Críticas & Falhas (Fardriver)**: Temperatura do Motor, Temperatura do Controlador Fardriver, Corrente de Linha e painel com histórico de códigos de falha catalogados (0 a 8).
  - **Pit Wall & Cronômetro de Voltas**: Cronômetro de precisão, marcação manual de voltas, melhor volta (*Best Lap*) e velocidade média.
  - **Monitor Serial ao Vivo**: Visualizador terminal embutido no modal da Porta Serial para acompanhamento de leituras brutas e logs de diagnóstico do microcontrolador diretamente pelo navegador.
- **Segurança & Controle de Acesso**:
  - **Modo Espectador**: Acesso aberto e seguro (somente leitura) para público e torcedores na internet, sem botões de controle de prova.
  - **Equipe Técnica**: Desbloqueio completo de controles (zerar cronômetro, gerenciar sessões e conectar rádio) protegido por senha (`leviata2026`).
- **Tolerância Zero a Dados Fictícios**:
  - O sistema opera estritamente com dados legítimos de hardware (sensores reais ou microcontrolador de teste). Não há dados gerados artificialmente por software.

---

## 🚀 Como Rodar na Pista (1 Clique)

Os arquivos executáveis `.bat` possuem detecção e liberação automática de porta, além de ambiente Node.js portátil integrado (zero dependências necessárias no Windows).

### 🎒 Modo 1: Operação Pista 100% Offline (Local)
Ideal para treinos ou provas sem necessidade de conexão com a internet.
1. Dê **2 cliques** no arquivo:
   ```cmd
   START_TELEMETRIA.bat
   ```
2. O servidor iniciará e o navegador abrirá automaticamente em `http://localhost:3001`. Os dados são gravados localmente no banco SQLite.

---

### 🌐 Modo 2: Operação Online Distribuída (Pista ➡️ Internet)
Permite que o **Computador B** (na pista, conectado ao rádio LoRa/ESP32 via USB) envie automaticamente todos os dados para o **Computador A** (na nuvem ou tenda central), permitindo que qualquer pessoa com celular ou notebook acompanhe a prova pela internet via link seguro do Cloudflare.

#### Passo 1: No Computador A (Servidor Central / Tenda)
1. Dê 2 cliques em:
   ```cmd
   START_SERVIDOR_ONLINE.bat
   ```
2. O servidor iniciará o túnel público do Cloudflare gerando uma URL segura (ex: `https://xxxx.trycloudflare.com`). Se as credenciais de e-mail estiverem preenchidas em `backend-node/config_online.json`, o link será enviado por e-mail automaticamente.

#### Passo 2: No Computador B (Estação de Pista com ESP32/LoRa)
1. Conecte o ESP32 via USB e dê 2 cliques em:
   ```cmd
   START_TELEMETRIA_ONLINE.bat
   ```
2. No painel aberto em `http://localhost:3001`, clique no botão **"Online Sync"** no topo da tela.
3. Cole o link público do Computador A e clique em **Aplicar URL**.
4. **Resiliência Total:** Se a internet na pista cair, os dados continuam salvos no disco do Computador B. Assim que o sinal retornar, a fila envia automaticamente todo o histórico pendente em lotes com confirmação de entrega (ACK) e sem duplicatas.

---

## 💾 Onde os Dados Ficam Salvos?

Todos os registros são salvos permanentemente em disco no arquivo:

📁 **`backend-node/telemetria.db`** (Banco SQLite 3)

### Estrutura das Variáveis Gravadas (28 Colunas):
- **Painel Solar:** `v_solar`, `i_solar`, `pot_solar`
- **Bateria LiFePO4:** `v_bat`, `soc`, `i_liq`
- **Propulsão / Fardriver:** `rpm`, `i_motor`, `t_motor`, `t_ctrl`, `falha_ctrl`
- **Navegação GPS:** `vel`, `lat`, `lon`, `proa`, `gps_satelites`, `gps_hora`, `hdop`
- **Conectividade:** `sinal_lora`, `sinal_lte`, `pkt_seq`
- **Controle & Auditoria:** `sessao_id`, `timestamp_iso`, `fonte`, `v_sist`, `status_data`, `uid` (identificador único para deduplicação), `enviado` (controle de fila)

### Como Visualizar e Exportar os Dados:
1. **Pela Interface Web (Exportar Planilha CSV):**
   - No topo do painel, clique no botão de **Sessões** e selecione **"Exportar CSV"**. Baixe a planilha completa com todas as voltas e dados segundo a segundo para abrir no Excel, Google Sheets, Python (Pandas) ou MATLAB.
2. **Direto no Banco SQLite:**
   - Use o software gratuito [DB Browser for SQLite](https://sqlitebrowser.org/) ou a extensão **SQLite Viewer** no VS Code para abrir diretamente o arquivo `telemetria.db`.

---

## 🛰️ Protocolo Serial JSON (ESP32 / LoRa Base)

A estação base recebe pela porta Serial USB (115200 bps) uma linha JSON formatada a cada 1 segundo:

```json
{
  "solar": {
    "tensao": 48.5,
    "corrente": 6.2,
    "pot": 300.7
  },
  "bateria": {
    "soc": 88.5,
    "tensao_bat": 51.8,
    "corrente_liq": -12.3
  },
  "prop": {
    "rpm": 1420,
    "i_motor": 18.5,
    "t_motor": 48,
    "t_ctrl": 39,
    "fardriver_falha": 0
  },
  "nav": {
    "vel": 18.4,
    "lat": -22.4154835,
    "lon": -41.8178226,
    "proa": 120.5,
    "gps_satelites": 12,
    "gps_hora": "18:45:00",
    "hdop": 0.8
  },
  "sinal": {
    "lora_pacotes": 142,
    "lora": -78
  }
}
```

---

## 💻 Simulador ESP32 de Bancada (`simulador_esp32_serial.ino`)

Para testes em bancada sem necessidade do barco estar na água, utilize o código Arduino incluído:

1. Abra o arquivo **`simulador_esp32_serial.ino`** na **Arduino IDE**.
2. Selecione a placa (ESP32 Dev Module / Heltec LoRa) e a porta COM.
3. Clique em **Upload (Carregar)**. *(Se aparecer `Connecting........`, segure o botão `BOOT` por 2 segundos).*
4. O ESP32 transmitirá variações dinâmicas de carga, velocidade e uma trajetória elíptica com proa realista ao redor do ponto oficial da **Lagoa de Imboassica** (`-22.4154835, -41.8178226`).

### Comandos de Teste no Monitor Serial:
Você pode simular falhas em tempo real enviando comandos pela serial:
- `FAULT:1` → Simula Sobretensão na Bateria.
- `FAULT:4` → Simula Superaquecimento do Motor (>85°C).
- `FAULT:7` → Simula Falha no Sinal do Acelerador.
- `CLEAR` → Limpa as falhas e retorna à operação normal.

---

## 🛠️ Ambiente de Desenvolvimento (Dev Mode)

Para desenvolvedores que desejam alterar o código:

### 1. Backend Node.js
```bash
cd "backend-node"
npm install
node server.js
```

### 2. Frontend React + Vite
```bash
cd "frontend-react"
npm install
npm run dev
```
Acesse `http://localhost:5173`. Para gerar o pacote de produção servido pelo Node.js:
```bash
npm run build
```

---

## 📂 Estrutura de Arquivos

```text
estação base web/
├── START_TELEMETRIA.bat           # Estação de Pista 100% Offline
├── START_TELEMETRIA_ONLINE.bat    # Estação de Pista com Fila de Sincronização Online
├── START_SERVIDOR_ONLINE.bat      # Servidor Central com Túnel Cloudflare e E-mail
├── simulador_esp32_serial.ino     # Firmware de teste para hardware ESP32
├── node/                          # Node.js portátil integrado para Windows
├── backend-node/                  # Servidor Express, SerialPort, SQLite3, Socket.IO
│   ├── server.js                  # API REST, WebSocket e rotas de ingestão
│   ├── serialManager.js           # Gerenciador da porta Serial USB com auto-reset
│   ├── database.js                # Banco SQLite (telemetria.db) com deduplicação
│   ├── uplink.js                  # Gerenciador de subida resiliente (Computador B)
│   ├── notificador_tunnel.js      # Gerenciador do túnel Cloudflare e envio de e-mail
│   └── telemetria.db              # Arquivo do banco de dados SQLite local
└── frontend-react/                # Interface React 19 + Vite
    ├── dist/                      # Build de produção servido diretamente pelo Express
    └── src/
        ├── components/            # Manômetros, Mapa, Bateria, Falhas, Monitor Serial
        └── pages/                 # DashboardPage e AnalyticsPage
```

---

## 🏆 Equipe Leviatã 2026 - Universidade do Estado do Amazonas (UEA)
*Engenharia e tecnologia amazonense desenvolvidas para o Desafio Solar Brasil.*
