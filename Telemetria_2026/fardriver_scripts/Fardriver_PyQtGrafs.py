import sys
import time
import struct
import threading
from collections import deque
import serial
import serial.tools.list_ports

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSlider, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import pyqtgraph as pg

# ==========================================
# CONFIGURAÇÕES E LIMITES (Motor 5KW + Chumbo 48V)
# ==========================================
BAUD_RATE = 19200
LIMIT_LINE_CURR = 100
LIMIT_PHASE_CURR = 450
LIMIT_RPM = 6000
LOW_VOLT_CUTOFF = 42.0
MAX_VOLT = 58.0

ERROS_FARDRIVER = {
    0: "NENHUM ERRO (SISTEMA OK)", 1: "FALHA SENSOR HALL DO MOTOR", 2: "FALHA NO ACELERADOR",
    3: "ALARME DE PROTEÇÃO ANORMAL", 4: "REINÍCIO POR PROTEÇÃO DE CORRENTE", 5: "FALHA DE TENSÃO (SUB/SOBRETENSÃO)",
    6: "RESERVADO", 7: "TEMPERATURA DO MOTOR ANORMAL", 8: "TEMPERATURA DA CONTROLADORA ANORMAL",
    9: "EXCESSO DE CORRENTE DE FASE", 10: "FALHA PONTO ZERO CORRENTE DE FASE", 11: "CURTO-CIRCUITO NA FASE DO MOTOR",
    12: "FALHA PONTO ZERO CORRENTE DE LINHA", 13: "FALHA MOSFET (PONTE SUPERIOR)", 14: "FALHA MOSFET (PONTE INFERIOR)",
    15: "PROTEÇÃO PICO DE CORRENTE DE LINHA"
}

# ==========================================
# ESTADO GLOBAL E PROTOCOLO FARDRIVER
# ==========================================
conexao = {"porta": None, "conectado": False, "serial_obj": None}
telemetry = {
    "rpm": 0, "volt": 0.0, "curr": 0.0, "phase_curr": 0.0, 
    "temp_motor": 0, "temp_mosfet": 0, "error": 0,
    "hall_a": False, "hall_b": False, "hall_c": False
}

CRC_TABLE_LO = [0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64]
CRC_TABLE_HI = [0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64]
FLASH_READ_ADDR = [0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0, 0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA]

def calc_crc(data_bytes):
    a, b = 0x3C, 0x7F
    for byte in data_bytes:
        crc_i = a ^ byte
        a, b = b ^ CRC_TABLE_HI[crc_i], CRC_TABLE_LO[crc_i]
    return bytes([a, b])

def check_crc(header_byte, data_bytes, crc_bytes):
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    crc_calc = calc_crc(full_msg)
    return crc_bytes[0] == crc_calc[0] and crc_bytes[1] == crc_calc[1]

def write_fardriver_param(ser, addr, data_payload):
    length = len(data_payload) + 4
    packet = bytearray([0xAA, 0xC0 + length, addr, addr])
    packet.extend(data_payload)
    crc = calc_crc(packet)
    packet.extend(crc)
    ser.write(packet)
    time.sleep(0.1)

# ==========================================
# THREAD DE LEITURA SERIAL
# ==========================================
def serial_reader():
    last_ka = time.time()
    buffer = b''

    while True:
        if conexao["conectado"] and conexao["porta"]:
            if conexao["serial_obj"] is None:
                try:
                    conexao["serial_obj"] = serial.Serial(conexao["porta"], BAUD_RATE, timeout=0.1)
                    conexao["serial_obj"].write(bytes([0xAA, 0x13, 0xEC, 0x07, 0x01, 0xF1, 0x48, 0xB7]))
                except Exception as e:
                    print(f"Erro ao abrir porta: {e}")
                    conexao["conectado"] = False
                    continue

            ser = conexao["serial_obj"]
            try:
                if time.time() - last_ka > 1.0:
                    ser.write(bytes([0xAA, 0x13, 0xEC, 0x07, 0x01, 0xF1, 0x48, 0xB7]))
                    last_ka = time.time()

                if ser.in_waiting:
                    buffer += ser.read(ser.in_waiting)
                
                while len(buffer) >= 16:
                    if buffer[0] != 0xAA:
                        buffer = buffer[1:]
                        continue
                    
                    pkt = buffer[:16]
                    header, data, crc = pkt[1], pkt[2:14], pkt[14:16]
                    
                    if check_crc(header, data, crc):
                        pkt_id = header & 0x3F
                        if pkt_id < len(FLASH_READ_ADDR):
                            addr = FLASH_READ_ADDR[pkt_id]
                            if addr == 0xE8:
                                telemetry["volt"] = struct.unpack_from('<h', data, 0)[0] / 10.0
                                telemetry["phase_curr"] = struct.unpack_from('<h', data, 2)[0] / 4.0
                                telemetry["curr"] = struct.unpack_from('<h', data, 4)[0] / 4.0
                            elif addr == 0xE2:
                                raw_rpm = struct.unpack_from('<h', data, 6)[0]
                                telemetry["rpm"] = abs(raw_rpm) if abs(raw_rpm) >= 20 else 0
                            elif addr == 0xF4:
                                telemetry["temp_motor"] = struct.unpack_from('<h', data, 0)[0]
                            elif addr == 0xD6:
                                telemetry["temp_mosfet"] = struct.unpack_from('<h', data, 10)[0]
                            elif addr == 0x0C:
                                telemetry["error"] = struct.unpack_from('<B', data, 0)[0]
                                
                                # Leitura do Estado dos Sensores Hall usando Bitmask (Igual ao Git em C++)
                                hall_byte = struct.unpack_from('<B', data, 1)[0]
                                telemetry["hall_a"] = bool(hall_byte & 0b00000001) # Fio Amarelo
                                telemetry["hall_b"] = bool(hall_byte & 0b00000010) # Fio Verde
                                telemetry["hall_c"] = bool(hall_byte & 0b00000100) # Fio Azul
                                
                        buffer = buffer[16:]
                    else:
                        buffer = buffer[1:]
                time.sleep(0.01)
                
            except serial.SerialException:
                conexao["conectado"] = False
                if conexao["serial_obj"]:
                    conexao["serial_obj"].close()
                    conexao["serial_obj"] = None
        else:
            if conexao["serial_obj"] is not None:
                conexao["serial_obj"].close()
                conexao["serial_obj"] = None
                telemetry["rpm"] = 0
                telemetry["volt"] = 0.0
                telemetry["curr"] = 0.0
                telemetry["phase_curr"] = 0.0
                telemetry["error"] = 0
                telemetry["hall_a"] = False
                telemetry["hall_b"] = False
                telemetry["hall_c"] = False
            time.sleep(0.5)

# ==========================================
# FOLHA DE ESTILOS E WIDGETS PERSONALIZADOS
# ==========================================
# FOLHA DE ESTILOS (TEMA ESCURO STREAMLIT)
# ==========================================
STYLESHEET = """
QMainWindow {
    background-color: #0E1117;
}
QLabel {
    color: #FAFAFA;
    font-family: "Segoe UI", Arial, sans-serif;
}
QFrame#Sidebar {
    background-color: #262730;
    border-right: 1px solid #333333;
}
QPushButton {
    background-color: #262730;
    color: white;
    border: 1px solid #4B4C52;
    padding: 8px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    border: 1px solid #FF4B4B;
    color: #FF4B4B;
}
QPushButton#BtnLigar:hover {
    border: 1px solid #00FF00;
    color: #00FF00;
}
QComboBox {
    background-color: #262730;
    color: white;
    border: 1px solid #4B4C52;
    padding: 5px;
    border-radius: 4px;
}
QSlider::groove:horizontal {
    border: 1px solid #4B4C52;
    height: 4px;
    background: #4B4C52;
    margin: 2px 0;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FF4B4B;
    border: 1px solid #FF4B4B;
    width: 14px;
    height: 14px;
    margin: -6px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #FF4B4B;
    border-radius: 2px;
}
"""

# ==========================================
# WIDGET PERSONALIZADO PARA AS MÉTRICAS
# ==========================================
class MetricCard(QFrame):
    def __init__(self, title, unit=""):
        super().__init__()
        self.unit = unit
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setFont(QFont("Segoe UI", 10))
        self.lbl_title.setStyleSheet("color: #A0A0A0;")
        
        self.lbl_value = QLabel(f"0 {self.unit}")
        self.lbl_value.setFont(QFont("Segoe UI", 28, QFont.Bold))
        
        self.lbl_delta = QLabel(" ")
        self.lbl_delta.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_delta)
        layout.addStretch()
        self.setLayout(layout)

    def update_data(self, value, delta_val, reverse_color=False):
        if isinstance(value, float):
            self.lbl_value.setText(f"{value:.1f} {self.unit}")
        else:
            self.lbl_value.setText(f"{value} {self.unit}")

        if delta_val == 0:
            self.lbl_delta.setText(" ")
            self.lbl_delta.setStyleSheet("background-color: transparent;")
            return

        is_positive = delta_val > 0
        seta = "↑" if is_positive else "↓"
        delta_str = f"{seta} {abs(delta_val):.1f} {self.unit}"
        self.lbl_delta.setText(delta_str)

        if (is_positive and not reverse_color) or (not is_positive and reverse_color):
            self.lbl_delta.setStyleSheet("color: #00FF00; background-color: rgba(0, 255, 0, 0.1); padding: 2px; border-radius: 3px;")
        else:
            self.lbl_delta.setStyleSheet("color: #FF4B4B; background-color: rgba(255, 75, 75, 0.1); padding: 2px; border-radius: 3px;")

# ==========================================
# WIDGET INDICADOR DOS SENSORES HALL (LEDS)
# ==========================================
class HallSensorsWidget(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 20, 0)
        
        lbl = QLabel("Hall:")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl.setStyleSheet("color: #A0A0A0;")
        layout.addWidget(lbl)

        self.led_a = QLabel("A")
        self.led_b = QLabel("B")
        self.led_c = QLabel("C")

        for led in (self.led_a, self.led_b, self.led_c):
            led.setFixedSize(30, 30)
            led.setAlignment(Qt.AlignCenter)
            led.setFont(QFont("Segoe UI", 10, QFont.Bold))
            led.setStyleSheet("background-color: #333333; color: white; border-radius: 15px;")
            layout.addWidget(led)

        self.setLayout(layout)

    def update_state(self, ha, hb, hc):
        # As cores originais dos fios de fase do motor BLDC
        c_a = "#FFD700" if ha else "#333333" # Fase A - Amarelo
        c_b = "#00FF00" if hb else "#333333" # Fase B - Verde
        c_c = "#00AAFF" if hc else "#333333" # Fase C - Azul
        
        texto_cor = "black" if ha else "white"
        self.led_a.setStyleSheet(f"background-color: {c_a}; color: {texto_cor}; border-radius: 15px;")
        
        texto_cor = "black" if hb else "white"
        self.led_b.setStyleSheet(f"background-color: {c_b}; color: {texto_cor}; border-radius: 15px;")
        
        texto_cor = "black" if hc else "white"
        self.led_c.setStyleSheet(f"background-color: {c_c}; color: {texto_cor}; border-radius: 15px;")


# ==========================================
# JANELA PRINCIPAL (MAIN APP)
# ==========================================
class FardriverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro - Telemetria PyQt")
        self.resize(1200, 700)
        self.setStyleSheet(STYLESHEET)
        
        # Para calcular os deltas (variações) entre as leituras
        self.prev_telemetry = {"rpm": 0, "volt": 0.0, "curr": 0.0, "phase_curr": 0.0, "temp_motor": 0, "temp_mosfet": 0}
        
        # Buffers para o Gráfico (PyQtGraph)
        self.max_pts = 100
        self.x_data = deque(range(self.max_pts), maxlen=self.max_pts)
        self.hist_rpm = deque([0]*self.max_pts, maxlen=self.max_pts)
        self.hist_curr = deque([0.0]*self.max_pts, maxlen=self.max_pts)
        self.hist_phase_curr = deque([0.0]*self.max_pts, maxlen=self.max_pts)
        self.hist_volt = deque([0.0]*self.max_pts, maxlen=self.max_pts)

        self._setup_ui()

        # Inicia a thread de leitura do cabo USB
        threading.Thread(target=serial_reader, daemon=True).start()

        # Configurar Timer para Atualização UI a 10 Hz (100ms)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_loop)

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ========================================
        # SIDEBAR (ESQUERDA)
        # ========================================
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(300)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(15)

        lbl_logo = QLabel("🐍 Fardriver Pro")
        lbl_logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        side_layout.addWidget(lbl_logo)

        lbl_ligacao = QLabel("Ligação USB")
        lbl_ligacao.setFont(QFont("Segoe UI", 12, QFont.Bold))
        side_layout.addWidget(lbl_ligacao)

        lbl_sel_porta = QLabel("Selecione a Porta COM:")
        side_layout.addWidget(lbl_sel_porta)

        self.cb_portas = QComboBox()
        portas = [port.device for port in serial.tools.list_ports.comports()]
        if not portas: portas = ["Nenhuma porta"]
        self.cb_portas.addItems(portas)
        side_layout.addWidget(self.cb_portas)

        self.btn_ligar = QPushButton("Ligar / Desligar")
        self.btn_ligar.setObjectName("BtnLigar")
        self.btn_ligar.clicked.connect(self.toggle_conexao)
        side_layout.addWidget(self.btn_ligar)

        self.lbl_status = QLabel("Desligado")
        self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        side_layout.addWidget(self.lbl_status)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: #4B4C52;")
        side_layout.addWidget(div)

        # Configurações Rápidas
        lbl_conf = QLabel("Configurações Rápidas")
        lbl_conf.setFont(QFont("Segoe UI", 12, QFont.Bold))
        side_layout.addWidget(lbl_conf)

        box_linha = QHBoxLayout()
        box_linha.addWidget(QLabel("Corrente de Bateria (A)"))
        self.val_linha = QLabel("80")
        self.val_linha.setStyleSheet("color: #FF4B4B; font-weight: bold;")
        box_linha.addWidget(self.val_linha, alignment=Qt.AlignRight)
        side_layout.addLayout(box_linha)
        
        self.sl_linha = QSlider(Qt.Horizontal)
        self.sl_linha.setRange(0, LIMIT_LINE_CURR)
        self.sl_linha.setValue(80)
        self.sl_linha.valueChanged.connect(lambda v: self.val_linha.setText(str(v)))
        side_layout.addWidget(self.sl_linha)

        box_fase = QHBoxLayout()
        box_fase.addWidget(QLabel("Corrente de Fase (A)"))
        self.val_fase = QLabel("250")
        self.val_fase.setStyleSheet("color: #FF4B4B; font-weight: bold;")
        box_fase.addWidget(self.val_fase, alignment=Qt.AlignRight)
        side_layout.addLayout(box_fase)

        self.sl_fase = QSlider(Qt.Horizontal)
        self.sl_fase.setRange(0, LIMIT_PHASE_CURR)
        self.sl_fase.setValue(250)
        self.sl_fase.valueChanged.connect(lambda v: self.val_fase.setText(str(v)))
        side_layout.addWidget(self.sl_fase)

        self.btn_gravar = QPushButton("Gravar na Controladora")
        self.btn_gravar.clicked.connect(self.gravar_parametros)
        side_layout.addWidget(self.btn_gravar)

        side_layout.addStretch()

        # ========================================
        # ÁREA PRINCIPAL (DIREITA)
        # ========================================
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        lbl_titulo = QLabel("⚡ Painel de Telemetria Fardriver")
        lbl_titulo.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_sub = QLabel("Monitorização em tempo real da ND72450 (Chumbo-Ácido Edition)")
        lbl_sub.setStyleSheet("color: #A0A0A0;")
        title_box.addWidget(lbl_titulo)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        # Painel Visual de Sensores Hall
        self.hall_widget = HallSensorsWidget()
        header_layout.addWidget(self.hall_widget, alignment=Qt.AlignTop)
        
        # Etiqueta de Erro
        self.lbl_erro = QLabel("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_erro.setStyleSheet("color: #A0A0A0;")
        header_layout.addWidget(self.lbl_erro, alignment=Qt.AlignTop)
        
        content_layout.addLayout(header_layout)

        # Métricas (Cards)
        metrics_layout = QHBoxLayout()
        self.card_rpm = MetricCard("Velocidade (RPM)", "rpm")
        self.card_volt = MetricCard("Tensão Bateria", "V")
        self.card_curr = MetricCard("Corrente Linha", "A")
        self.card_phase = MetricCard("Corrente Fase", "A")
        self.card_temp = MetricCard("Temp Motor", "°C")
        
        metrics_layout.addWidget(self.card_rpm)
        metrics_layout.addWidget(self.card_volt)
        metrics_layout.addWidget(self.card_curr)
        metrics_layout.addWidget(self.card_phase)
        metrics_layout.addWidget(self.card_temp)
        
        content_layout.addLayout(metrics_layout)

        # Gráficos (PyQtGraph)
        lbl_graf = QLabel("Gráficos de Desempenho")
        lbl_graf.setFont(QFont("Segoe UI", 16, QFont.Bold))
        content_layout.addWidget(lbl_graf)

        charts_layout = QHBoxLayout()
        pg.setConfigOption('background', '#0E1117')
        pg.setConfigOption('foreground', '#A0A0A0')

        # Gráfico 1: Tensão
        self.plot_volt = pg.PlotWidget(title="Tensão da Bateria (V)")
        self.plot_volt.showGrid(x=False, y=True, alpha=0.2)
        self.plot_volt.setMouseEnabled(x=False, y=False)
        self.plot_volt.getAxis('bottom').setStyle(showValues=False)
        self.plot_volt.setYRange(LOW_VOLT_CUTOFF - 2, MAX_VOLT + 5)
        self.line_volt = self.plot_volt.plot(pen=pg.mkPen(color='#00AAFF', width=2))

        # Gráfico 2: Corrente
        self.plot_curr = pg.PlotWidget(title="Correntes (A)")
        self.plot_curr.showGrid(x=False, y=True, alpha=0.2)
        self.plot_curr.setMouseEnabled(x=False, y=False)
        self.plot_curr.addLegend(offset=(10, 10))
        self.plot_curr.getAxis('bottom').setStyle(showValues=False)
        self.plot_curr.setYRange(-5, LIMIT_PHASE_CURR + 20)
        self.line_curr = self.plot_curr.plot(pen=pg.mkPen(color='#FF4B4B', width=2), name="Linha")
        self.line_phase = self.plot_curr.plot(pen=pg.mkPen(color='#FFAA00', width=2), name="Fase")
        
        # Gráfico 3: Rotação (RPM)
        self.plot_rpm = pg.PlotWidget(title="Velocidade (RPM)")
        self.plot_rpm.showGrid(x=False, y=True, alpha=0.2)
        self.plot_rpm.setMouseEnabled(x=False, y=False)
        self.plot_rpm.getAxis('bottom').setStyle(showValues=False)
        self.plot_rpm.setYRange(0, LIMIT_RPM + 500)
        self.line_rpm = self.plot_rpm.plot(pen=pg.mkPen(color='#00FF00', width=2))

        # Adicionar os 3 gráficos ao layout horizontal
        charts_layout.addWidget(self.plot_volt)
        charts_layout.addWidget(self.plot_curr)
        charts_layout.addWidget(self.plot_rpm)
        
        content_layout.addLayout(charts_layout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    def toggle_conexao(self):
        porta = self.cb_portas.currentText()
        if porta == "Nenhuma porta":
            return

        # Interage com a variável global para a Thread Serial reagir
        if not conexao["conectado"]:
            conexao["porta"] = porta
            conexao["conectado"] = True
            
            self.lbl_status.setText(f"Ligado na {porta}")
            self.lbl_status.setStyleSheet("background-color: rgba(0, 255, 0, 0.1); color: #00FF00; padding: 10px; border-radius: 4px; font-weight: bold;")
            self.btn_ligar.setText("Desligar")
            self.timer.start(100) # Inicia UI loop
        else:
            conexao["conectado"] = False
            self.lbl_status.setText("Desligado")
            self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;")
            self.lbl_erro.setText("AGUARDAR LIGAÇÃO...")
            self.lbl_erro.setStyleSheet("color: #A0A0A0;")
            self.btn_ligar.setText("Ligar / Desligar")
            self.timer.stop()

    def gravar_parametros(self):
        if not conexao["conectado"] or conexao["serial_obj"] is None:
            QMessageBox.warning(self, "Erro", "Ligue a controladora primeiro para gravar!")
            return

        line_curr_val = self.sl_linha.value()
        phase_curr_val = self.sl_fase.value()

        resposta = QMessageBox.question(self, "Confirmar Gravação", 
                                       f"Vai gravar os seguintes limites:\n\nBateria: {line_curr_val} A\nFase: {phase_curr_val} A\n\nTem a certeza?",
                                       QMessageBox.Yes | QMessageBox.No)

        if resposta == QMessageBox.Yes:
            try:
                # Blocos de acordo com a engenharia reversa Fardriver
                # MaxLineCurr fica no bloco 0x18, MaxPhaseCurr no bloco 0x2A
                val_linha_hex = struct.pack('<H', line_curr_val * 4)
                val_fase_hex = struct.pack('<H', phase_curr_val * 4)
                print(f"A preparar gravação. Linha: {val_linha_hex.hex()}, Fase: {val_fase_hex.hex()}")
                QMessageBox.information(self, "Sucesso", "Comandos enviados para a controladora (Requer comando Save 0xFE para manter).")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Gravação", f"Ocorreu um erro:\n{e}")

    def update_telemetry_loop(self):
        """Atualiza a UI lendo a telemetria real vinda da Thread Serial"""
        global telemetry
        t = telemetry
        
        # Se a ligação cair fisicamente (cabo arrancado), a Thread Serial baixa o status
        if not conexao["conectado"] and self.timer.isActive():
            self.toggle_conexao() # Desliga a interface automaticamente
            return
            
        # Gestão de Erros Fardriver
        cod_erro = t["error"]
        if cod_erro == 0:
            self.lbl_erro.setText(ERROS_FARDRIVER[0])
            self.lbl_erro.setStyleSheet("color: #00FF00;")
        else:
            texto_erro = ERROS_FARDRIVER.get(cod_erro, f"ERRO DESCONHECIDO ({cod_erro})")
            cor = "#FF4B4B" if int(time.time() * 2) % 2 == 0 else "#FFAA00" # Efeito piscar
            self.lbl_erro.setText(f"⚠️ {texto_erro}")
            self.lbl_erro.setStyleSheet(f"color: {cor};")

        # Cálculos de Deltas (Variação em relação ao ciclo de 100ms anterior)
        delta_rpm = t["rpm"] - self.prev_telemetry["rpm"]
        delta_volt = t["volt"] - self.prev_telemetry["volt"]
        delta_curr = t["curr"] - self.prev_telemetry["curr"]
        delta_phase = t["phase_curr"] - self.prev_telemetry["phase_curr"]
        delta_temp = t["temp_motor"] - self.prev_telemetry["temp_motor"]

        # Atualiza Cartões (Métricas)
        self.card_rpm.update_data(t["rpm"], delta_rpm)
        self.card_volt.update_data(t["volt"], delta_volt)
        self.card_curr.update_data(t["curr"], delta_curr, reverse_color=True)
        self.card_phase.update_data(t["phase_curr"], delta_phase, reverse_color=True)
        self.card_temp.update_data(t["temp_motor"], delta_temp, reverse_color=True)

        # Atualiza LEDs dos Sensores Hall
        self.hall_widget.update_state(t["hall_a"], t["hall_b"], t["hall_c"])

        # Atualiza a memória para o próximo ciclo
        self.prev_telemetry = t.copy()

        # Atualiza Arrays do Gráfico
        self.hist_rpm.append(t["rpm"])
        self.hist_curr.append(t["curr"])
        self.hist_phase_curr.append(t["phase_curr"])
        self.hist_volt.append(t["volt"])

        # Redesenha Gráficos PyQtGraph (Super Rápido!)
        self.line_rpm.setData(list(self.x_data), list(self.hist_rpm))
        self.line_curr.setData(list(self.x_data), list(self.hist_curr))
        self.line_phase.setData(list(self.x_data), list(self.hist_phase_curr))
        self.line_volt.setData(list(self.x_data), list(self.hist_volt))