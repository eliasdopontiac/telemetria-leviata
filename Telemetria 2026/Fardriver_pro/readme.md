# ⛵ Telemetria 2026 - Comunicação Fardriver 🔋

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Serial](https://img.shields.io/badge/Comunicação-Serial-green)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-orange)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Equipe](https://img.shields.io/badge/Equipe-Leviatã%20UEA-red)

Bem-vindo ao diretório de **Telemetria (Temporada 2026)** da **Equipe Leviatã (UEA)**.  

Este repositório centraliza todo o **ecossistema de software desenvolvido para aquisição de dados do veículo**, com foco na **comunicação serial com o controlador Fardriver**.

O sistema evoluiu de **scripts experimentais** para uma **aplicação estruturada com dashboard em tempo real**, permitindo acompanhar **parâmetros críticos do motor** durante testes e competições como o **Desafio Solar Brasil**.

---

# 📊 Dashboard

A aplicação possui uma **interface gráfica em tempo real** para monitoramento dos dados do controlador.

![Dashboard](dashboard.png)

*(adicione aqui uma captura da interface do sistema)*

---

# 🏗️ Arquitetura do Sistema

A arquitetura do sistema é dividida em três camadas principais:

```
Fardriver Controller
        │
        │ Serial (19200 bps)
        │
USB-TTL Adapter
        │
        │
Python Application
        │
 ├── Serial Communication
 │
 ├── Packet Parser (CRC / Checksum)
 │
 └── Dashboard UI
```

Fluxo de funcionamento:

1. O **controlador Fardriver** envia pacotes pela interface serial  
2. O módulo **fardriver_serial.py** recebe os dados  
3. O **heb_parser.py** decodifica e valida os pacotes  
4. A **ui_dashboard.py** atualiza os valores em tempo real  

---

# 📁 Estrutura do Diretório

O projeto está dividido entre a **versão consolidada da aplicação** e **scripts de prototipagem**.

## 📦 Fardriver_pro/

Núcleo do sistema pronto para execução.

```
Fardriver_pro/
│
├── main.py
├── fardriver_serial.py
├── heb_parser.py
├── ui_dashboard.py
│
├── FardriverPro.spec
└── dist/
```

Arquivos principais:

- **main.py**  
  Ponto de entrada da aplicação.

- **fardriver_serial.py**  
  Gerencia comunicação serial e sistema Keep-Alive.

- **heb_parser.py**  
  Decodifica e valida pacotes do protocolo Fardriver.

- **ui_dashboard.py**  
  Interface gráfica em tempo real.

- **dist/**  
  Executável gerado com **PyInstaller**.

---

## 🧪 Scripts de Prototipagem

Experimentos realizados durante o desenvolvimento da dashboard.

```
Fardriver_matplotlib.py
Fardriver_PyQtGrafs.py
fardriver_streamlit.py
```

---

## 🧱 Primeiras versões

Primeiras tentativas de leitura serial e interface.

```
Fardriver.py
fardriver_app.py
fardriver_UI_teste.py
```

---

# ⚙️ Tecnologias Utilizadas

### Linguagem

- Python

### Bibliotecas

- PyQt5
- Matplotlib
- Streamlit
- PySerial

### Comunicação

- Serial via **USB-TTL**

### Configuração Serial

```
Baud Rate: 19200
Data Bits: 8
Parity: None
Stop Bits: 1
```

### Estrutura do Protocolo Fardriver

```
Header → Length → Payload → CRC → End Byte
```

---

# 🛠️ Funcionalidades

- [x] Leitura de **RPM**
- [x] Monitoramento de **tensão do sistema**
- [x] Monitoramento de **corrente**
- [x] Monitoramento de **temperatura**
- [x] Validação de pacotes via **CRC**
- [x] Interface gráfica em tempo real
- [x] Geração de executável standalone

---

# 📦 Instalação

Certifique-se de ter o **Python instalado**.

Instale as dependências:

```bash
pip install pyserial PyQt5 matplotlib streamlit
```

---

# 🔌 Conexão com o Controlador

Use um **adaptador USB-TTL**.

Conexões necessárias:

```
TX (Fardriver)  -> RX (PC)
RX (Fardriver)  -> TX (PC)
GND (Fardriver) -> GND (PC)
```

---

# ▶️ Execução

## Modo desenvolvimento

```
cd Fardriver_pro
python main.py
```

---

## Executável

A versão compilada está em:

```
Fardriver_pro/dist/
```

Basta executar o `.exe`.

---

# 👨‍🔧 Equipe

**Elias Cunha**  
Electrical Lead — Equipe Leviatã

📧 ehlc.eai22@uea.edu.br  

📸 Instagram  
@leviatauea

---

# 🌿 Sobre a Equipe Leviatã

A **Equipe Leviatã (UEA)** desenvolve tecnologias voltadas à **mobilidade sustentável**, participando de competições como o **Desafio Solar Brasil**, promovendo inovação tecnológica na Amazônia.

---

⭐ Desenvolvido com foco em **engenharia, inovação e sustentabilidade na Amazônia**