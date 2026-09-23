# ⚡ Telemetria Leviatã — Temporada 2026

Este diretório contém **todo o ecossistema de software e firmware** desenvolvido pela Equipe Leviatã para a temporada de competição 2026 do Desafio Solar Brasil.

## 🗂️ Estrutura

```
Telemetria_2026/
│
├── estação base/          ← ⭐ Sistema principal de telemetria em tempo real
│   ├── estação base web/  ← Aplicação Web (Node.js + React) — PRODUÇÃO
│   │   ├── backend-node/  ← API REST + Serial + SQLite + Socket.IO
│   │   ├── frontend-react/← Dashboard React (Vite + Tailwind)
│   │   └── START_TELEMETRIA.bat ← Inicialização com 1 clique
│   └── LoRa Base/         ← Firmware da estação base LoRa (ESP32)
│
├── Firmware/              ← Firmwares embarcados (pasta geral)
│
├── Firmware Heltec esp32 LoRa sx1276/
│   └── Firmware_LoRa_Central_Hub.ino ← Hub central LoRa (2 canais)
│
├── Firmware lilygo esp32 sim7000g/
│   ├── Firmware_LilyGO_Gateway_LTE.ino ← Gateway LTE / MQTT
│   └── Firmware_SIM7000G_BMV.ino       ← Leitura BMV via LTE
│
├── Fardriver_pro/         ← Dashboard Python do controlador de motor (PyQt5)
│
└── fardriver_scripts/     ← Scripts de prototipagem e análise do Fardriver
```

---

## 🚀 Como Iniciar — Estação Base (Produção)

> Requer: Node.js instalado **ou** usar o Node.js portátil embutido no ZIP.

1. Navegue até `estação base/estação base web/`
2. Execute `START_TELEMETRIA.bat` (duplo clique)
3. O navegador abrirá automaticamente em `http://localhost:3001`
4. Para conectar o rádio LoRa: clique em **"Serial Server"** no painel

---

## 📡 Arquitetura de Comunicação 2026

```
[Barco]──LoRa──[ESP32 Estação Base]──USB──[Backend Node.js]──WebSocket──[Dashboard React]
                                                │
                                           SQLite .db
                                     (histórico persistente)
```

---

## 🛠️ Sub-sistemas

| Componente | Tecnologia | Propósito |
|---|---|---|
| Estação Base Web | Node.js + React + SQLite | Dashboard em tempo real + histórico |
| Firmware LoRa Base | C++ (ESP32) | Recepção dos pacotes LoRa do barco |
| Firmware Heltec Hub | C++ (Heltec ESP32) | Roteador LoRa multi-canal |
| Firmware LilyGO LTE | C++ (LilyGO SIM7000G) | Gateway LTE / MQTT como backup |
| Fardriver Pro | Python + PyQt5 | Diagnóstico e logs do controlador BLDC |
