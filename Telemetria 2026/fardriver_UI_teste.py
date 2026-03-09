import sys
import time
import random
from collections import deque

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSlider, QFrame, QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import pyqtgraph as pg

# ==========================================
# CONFIGURAÇÕES E LIMITES (Motor 5KW + Chumbo 48V)
# ==========================================
LIMIT_LINE_CURR = 100
LIMIT_PHASE_CURR = 450
LIMIT_RPM = 6000
LOW_VOLT_CUTOFF = 42.0
MAX_VOLT = 58.0

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
QPushButton:disabled {
    background-color: #1a1b20;
    color: #555555;
    border: 1px solid #333333;
}
QPushButton#BtnLigar:hover {
    border: 1px solid #00FF00;
    color: #00FF00;
}
QPushButton#BtnAutoLearn {
    background-color: #FF8C00;
    color: white;
    border: 1px solid #CC7000;
}
QPushButton#BtnAutoLearn:hover {
    background-color: #CC7000;
    border: 1px solid #FF8C00;
}
QPushButton#BtnAutoLearn:disabled {
    background-color: #1a1b20;
    color: #555555;
    border: 1px solid #333333;
}
QComboBox {
    background-color: #262730;
    color: white;
    border: 1px solid #4B4C52;
    padding: 5px;
    border-radius: 4px;
}
QComboBox:disabled {
    background-color: #1a1b20;
    color: #555555;
    border: 1px solid #333333;
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

/* Estilos para quando o slider está bloqueado */
QSlider::groove:horizontal:disabled {
    background: #333333;
    border: 1px solid #333333;
}
QSlider::handle:horizontal:disabled {
    background: #555555;
    border: 1px solid #555555;
}
QSlider::sub-page:horizontal:disabled {
    background: #555555;
}

/* ScrollBar Transparente estilo Moderno */
QScrollArea {
    border: none;
    background-color: transparent;
}
QFrame#ScrollContent {
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #262730;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #4B4C52;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #FF4B4B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
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
        self.lbl_value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
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
# JANELA PRINCIPAL (MAIN APP) - APENAS UI
# ==========================================
class FardriverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro - UI Simulada (Sem Serial)")
        self.resize(1200, 750)
        self.setStyleSheet(STYLESHEET)
        
        # Variáveis de controlo da UI
        self.conectado = False
        
        # Estado simulado inicial
        self.telemetry = {
            "rpm": 0, "volt": 48.0, "curr": 0.0, "power": 0.0, "phase_curr": 0.0, 
            "temp_motor": 25, "temp_mosfet": 30, "throttle": 0.8,
            "hall_a": False, "hall_b": False, "hall_c": False
        }
        
        self.prev_telemetry = self.telemetry.copy()
        
        # Buffers para o Gráfico (PyQtGraph)
        self.max_pts = 100
        self.x_data = deque(range(self.max_pts), maxlen=self.max_pts)
        self.hist_rpm = deque([0]*self.max_pts, maxlen=self.max_pts)
        self.hist_curr = deque([0.0]*self.max_pts, maxlen=self.max_pts)
        self.hist_volt = deque([48.0]*self.max_pts, maxlen=self.max_pts)

        self._setup_ui()

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
        sidebar.setFixedWidth(320) # Aumentado ligeiramente para a scrollbar
        side_main_layout = QVBoxLayout(sidebar)
        side_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Cabeçalho Fixo da Sidebar
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 10)
        
        lbl_logo = QLabel("🐍 Fardriver Pro")
        lbl_logo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header_layout.addWidget(lbl_logo)

        lbl_ligacao = QLabel("Ligação USB (Simulada)")
        lbl_ligacao.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header_layout.addWidget(lbl_ligacao)

        self.cb_portas = QComboBox()
        self.cb_portas.addItems(["COM1 (Simulação)", "COM2 (Simulação)"])
        header_layout.addWidget(self.cb_portas)

        self.btn_ligar = QPushButton("Ligar / Desligar")
        self.btn_ligar.setObjectName("BtnLigar")
        self.btn_ligar.clicked.connect(self.toggle_conexao)
        header_layout.addWidget(self.btn_ligar)

        self.lbl_status = QLabel("Desligado")
        self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.lbl_status)
        
        side_main_layout.addWidget(header_frame)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: #4B4C52; margin: 0px 20px;")
        side_main_layout.addWidget(div)

        # ----------------------------------------
        # ZONA COM SCROLL (Para dezenas de configurações)
        # ----------------------------------------
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QFrame()
        scroll_content.setObjectName("ScrollContent")
        side_layout = QVBoxLayout(scroll_content)
        side_layout.setContentsMargins(20, 10, 20, 20)
        side_layout.setSpacing(15)
        
        # Cabeçalho Configurações
        box_conf_header = QHBoxLayout()
        lbl_conf = QLabel("Afinação Motor")
        lbl_conf.setFont(QFont("Segoe UI", 12, QFont.Bold))
        box_conf_header.addWidget(lbl_conf)
        
        self.btn_lock = QPushButton("🔒 Desbloq.")
        self.btn_lock.setFixedWidth(95)
        self.btn_lock.clicked.connect(self.toggle_lock_sliders)
        box_conf_header.addWidget(self.btn_lock, alignment=Qt.AlignRight)
        side_layout.addLayout(box_conf_header)

        # Corrente Linha
        box_linha = QHBoxLayout()
        box_linha.addWidget(QLabel("Corrente Bateria (A)"))
        self.val_linha = QLabel("80")
        self.val_linha.setStyleSheet("color: #FF4B4B; font-weight: bold;")
        box_linha.addWidget(self.val_linha, alignment=Qt.AlignRight)
        side_layout.addLayout(box_linha)
        self.sl_linha = QSlider(Qt.Horizontal)
        self.sl_linha.setRange(0, LIMIT_LINE_CURR)
        self.sl_linha.setValue(80)
        self.sl_linha.setEnabled(False)
        self.sl_linha.valueChanged.connect(lambda v: self.val_linha.setText(str(v)))
        side_layout.addWidget(self.sl_linha)

        # Corrente Fase
        box_fase = QHBoxLayout()
        box_fase.addWidget(QLabel("Corrente Fase (A)"))
        self.val_fase = QLabel("250")
        self.val_fase.setStyleSheet("color: #FF4B4B; font-weight: bold;")
        box_fase.addWidget(self.val_fase, alignment=Qt.AlignRight)
        side_layout.addLayout(box_fase)
        self.sl_fase = QSlider(Qt.Horizontal)
        self.sl_fase.setRange(0, LIMIT_PHASE_CURR)
        self.sl_fase.setValue(250)
        self.sl_fase.setEnabled(False)
        self.sl_fase.valueChanged.connect(lambda v: self.val_fase.setText(str(v)))
        side_layout.addWidget(self.sl_fase)

        # Freio Regenerativo (EBS)
        box_regen = QHBoxLayout()
        box_regen.addWidget(QLabel("Freio Regen (A)"))
        self.val_regen = QLabel("30")
        self.val_regen.setStyleSheet("color: #00AAFF; font-weight: bold;") # Azul para diferenciar travagem
        box_regen.addWidget(self.val_regen, alignment=Qt.AlignRight)
        side_layout.addLayout(box_regen)
        self.sl_regen = QSlider(Qt.Horizontal)
        self.sl_regen.setRange(0, 100)
        self.sl_regen.setValue(30)
        self.sl_regen.setEnabled(False)
        self.sl_regen.valueChanged.connect(lambda v: self.val_regen.setText(str(v)))
        side_layout.addWidget(self.sl_regen)

        div2 = QFrame()
        div2.setFrameShape(QFrame.HLine)
        div2.setStyleSheet("background-color: #333333;")
        side_layout.addWidget(div2)

        # Enfraquecimento de Campo (WeakA)
        lbl_weaka = QLabel("Enfraquecimento (WeakA):")
        side_layout.addWidget(lbl_weaka)
        self.cb_weaka = QComboBox()
        self.cb_weaka.addItems(["Nível 0 (Desligado)", "Nível 1 (Leve)", "Nível 2 (Médio)", "Nível 3 (Máximo)"])
        self.cb_weaka.setCurrentText("Nível 0 (Desligado)")
        self.cb_weaka.setEnabled(False)
        side_layout.addWidget(self.cb_weaka)

        # Resposta do Acelerador
        lbl_throttle = QLabel("Curva de Aceleração:")
        side_layout.addWidget(lbl_throttle)
        self.cb_throttle = QComboBox()
        self.cb_throttle.addItems(["Line", "Sport", "ECO"])
        self.cb_throttle.setCurrentText("Line")
        self.cb_throttle.setEnabled(False)
        side_layout.addWidget(self.cb_throttle)

        # Pares de Polos
        box_polos = QHBoxLayout()
        box_polos.addWidget(QLabel("Pares de Polos:"))
        self.val_polos = QLabel("4")
        self.val_polos.setStyleSheet("color: white; font-weight: bold;")
        box_polos.addWidget(self.val_polos, alignment=Qt.AlignRight)
        side_layout.addLayout(box_polos)
        self.sl_polos = QSlider(Qt.Horizontal)
        self.sl_polos.setRange(1, 40)
        self.sl_polos.setValue(4) # Padrão seguro para motores HPM
        self.sl_polos.setEnabled(False)
        self.sl_polos.valueChanged.connect(lambda v: self.val_polos.setText(str(v)))
        side_layout.addWidget(self.sl_polos)

        # Sensor de Temperatura do Motor
        lbl_sensor = QLabel("Sensor Temp. Motor:")
        side_layout.addWidget(lbl_sensor)
        self.cb_sensor_temp = QComboBox()
        self.cb_sensor_temp.addItems(["Desativado", "KTY83-122", "KTY84-130", "KTY84-150", "PT1000", "NTC10K"])
        self.cb_sensor_temp.setCurrentText("KTY84-130")
        self.cb_sensor_temp.setEnabled(False)
        side_layout.addWidget(self.cb_sensor_temp)

        side_layout.addStretch()

        # Botões de Ação Fixos no fundo do Scroll
        self.btn_gravar = QPushButton("⬇ Gravar na Controladora")
        self.btn_gravar.setEnabled(False)
        self.btn_gravar.clicked.connect(self.gravar_parametros)
        side_layout.addWidget(self.btn_gravar)

        self.btn_autolearn = QPushButton("⚙️ Iniciar Auto-Aprendizado")
        self.btn_autolearn.setObjectName("BtnAutoLearn")
        self.btn_autolearn.setEnabled(False)
        self.btn_autolearn.clicked.connect(self.iniciar_autolearn)
        side_layout.addWidget(self.btn_autolearn)

        scroll_area.setWidget(scroll_content)
        side_main_layout.addWidget(scroll_area)

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
        lbl_sub = QLabel("Modo Design: Monitorização simulada para testes de UI")
        lbl_sub.setStyleSheet("color: #A0A0A0;")
        title_box.addWidget(lbl_titulo)
        title_box.addWidget(lbl_sub)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        
        self.hall_widget = HallSensorsWidget()
        header_layout.addWidget(self.hall_widget, alignment=Qt.AlignTop)
        
        self.lbl_erro = QLabel("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_erro.setStyleSheet("color: #A0A0A0;")
        header_layout.addWidget(self.lbl_erro, alignment=Qt.AlignTop)
        
        content_layout.addLayout(header_layout)

        # ========================================
        # MÉTRICAS (CARDS) - DIVIDIDAS EM 2 LINHAS
        # ========================================
        metrics_layout_top = QHBoxLayout()
        self.card_rpm = MetricCard("Rotação Motor", "RPM")
        self.card_volt = MetricCard("Tensão Bateria", "V")
        self.card_curr = MetricCard("Corrente Linha", "A")
        self.card_power = MetricCard("Potência Inst.", "W")
        
        metrics_layout_top.addWidget(self.card_rpm)
        metrics_layout_top.addWidget(self.card_volt)
        metrics_layout_top.addWidget(self.card_curr)
        metrics_layout_top.addWidget(self.card_power)
        
        metrics_layout_bot = QHBoxLayout()
        self.card_temp = MetricCard("Temp Motor", "°C")
        self.card_temp_ctrl = MetricCard("Temp Controladora", "°C")
        self.card_throttle = MetricCard("Acelerador", "V")
        
        metrics_layout_bot.addWidget(self.card_temp)
        metrics_layout_bot.addWidget(self.card_temp_ctrl)
        metrics_layout_bot.addWidget(self.card_throttle)
        metrics_layout_bot.addStretch()
        
        content_layout.addLayout(metrics_layout_top)
        content_layout.addLayout(metrics_layout_bot)

        # ========================================
        # GRÁFICOS (PYQTGRAPH)
        # ========================================
        lbl_graf = QLabel("Gráficos de Desempenho")
        lbl_graf.setFont(QFont("Segoe UI", 16, QFont.Bold))
        content_layout.addWidget(lbl_graf)

        charts_layout = QHBoxLayout()
        pg.setConfigOption('background', '#0E1117')
        pg.setConfigOption('foreground', '#A0A0A0')

        self.plot_volt = pg.PlotWidget(title="Tensão da Bateria (V)")
        self.plot_volt.showGrid(x=False, y=True, alpha=0.2)
        self.plot_volt.setMouseEnabled(x=False, y=False)
        self.plot_volt.getAxis('bottom').setStyle(showValues=False)
        self.plot_volt.setYRange(LOW_VOLT_CUTOFF - 2, MAX_VOLT + 5)
        self.line_volt = self.plot_volt.plot(pen=pg.mkPen(color='#00AAFF', width=2))

        self.plot_curr = pg.PlotWidget(title="Corrente de Linha (A)")
        self.plot_curr.showGrid(x=False, y=True, alpha=0.2)
        self.plot_curr.setMouseEnabled(x=False, y=False)
        self.plot_curr.getAxis('bottom').setStyle(showValues=False)
        self.plot_curr.setYRange(-5, LIMIT_LINE_CURR + 20)
        self.line_curr = self.plot_curr.plot(pen=pg.mkPen(color='#FF4B4B', width=2))
        
        self.plot_rpm = pg.PlotWidget(title="Rotação do Motor (RPM)")
        self.plot_rpm.showGrid(x=False, y=True, alpha=0.2)
        self.plot_rpm.setMouseEnabled(x=False, y=False)
        self.plot_rpm.getAxis('bottom').setStyle(showValues=False)
        self.plot_rpm.setYRange(0, LIMIT_RPM + 500)
        self.line_rpm = self.plot_rpm.plot(pen=pg.mkPen(color='#00FF00', width=2))

        charts_layout.addWidget(self.plot_volt)
        charts_layout.addWidget(self.plot_curr)
        charts_layout.addWidget(self.plot_rpm)
        
        content_layout.addLayout(charts_layout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

    def toggle_lock_sliders(self):
        widgets_to_toggle = [
            self.sl_linha, self.sl_fase, self.sl_regen, 
            self.cb_weaka, self.cb_throttle, self.sl_polos, 
            self.cb_sensor_temp, self.btn_gravar, self.btn_autolearn
        ]
        
        if "Desbloq" in self.btn_lock.text():
            self.btn_lock.setText("🔓 Bloquear")
            self.btn_lock.setStyleSheet("color: #FF4B4B; border: 1px solid #FF4B4B;")
            for w in widgets_to_toggle: w.setEnabled(True)
        else:
            self.btn_lock.setText("🔒 Desbloq.")
            self.btn_lock.setStyleSheet("")
            for w in widgets_to_toggle: w.setEnabled(False)

    def toggle_conexao(self):
        porta = self.cb_portas.currentText()
        if not porta:
            return

        if not self.conectado:
            self.conectado = True
            self.lbl_status.setText(f"Ligado na {porta}")
            self.lbl_status.setStyleSheet("background-color: rgba(0, 255, 0, 0.1); color: #00FF00; padding: 10px; border-radius: 4px; font-weight: bold;")
            self.btn_ligar.setText("Desligar")
            self.lbl_erro.setText("SISTEMA OK (SIMULADO)")
            self.lbl_erro.setStyleSheet("color: #00FF00;")
            self.timer.start(100)
        else:
            self.conectado = False
            self.lbl_status.setText("Desligado")
            self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;")
            self.lbl_erro.setText("AGUARDAR LIGAÇÃO...")
            self.lbl_erro.setStyleSheet("color: #A0A0A0;")
            self.btn_ligar.setText("Ligar / Desligar")
            self.timer.stop()
            self.hall_widget.update_state(False, False, False)

    def gravar_parametros(self):
        if not self.conectado:
            QMessageBox.warning(self, "Erro", "Ligue a simulação primeiro para gravar!")
            return

        # Resumo do que vai ser gravado
        resumo = (
            f"Bateria: {self.sl_linha.value()} A\n"
            f"Fase: {self.sl_fase.value()} A\n"
            f"Regen EBS: {self.sl_regen.value()} A\n"
            f"Pares Polos: {self.sl_polos.value()}\n"
            f"WeakA: {self.cb_weaka.currentText()}\n"
            f"Acelerador: {self.cb_throttle.currentText()}\n"
            f"Sensor Temp.: {self.cb_sensor_temp.currentText()}\n"
        )

        resposta = QMessageBox.question(self, "Confirmar Gravação", 
                                       f"Vai gravar os seguintes parâmetros:\n\n{resumo}\nTem a certeza?",
                                       QMessageBox.Yes | QMessageBox.No)

        if resposta == QMessageBox.Yes:
            QMessageBox.information(self, "Sucesso", "Parâmetros guardados na interface (Modo Simulação).")

    def iniciar_autolearn(self):
        if not self.conectado:
            QMessageBox.warning(self, "Erro", "Ligue a simulação primeiro!")
            return

        resposta = QMessageBox.question(self, "INSTRUÇÕES - AUTO APRENDIZADO", 
            "ATENÇÃO - PROCEDIMENTO DE CALIBRAÇÃO!\n\n"
            "1. Coloque a moto no descanso central (roda livre).\n"
            "2. Clique em 'Yes' abaixo para enviar o comando.\n"
            "3. Em seguida, ACELERE AO MÁXIMO E SEGURE.\n\n"
            "Deseja iniciar o procedimento agora?",
            QMessageBox.Yes | QMessageBox.No)

        if resposta == QMessageBox.Yes:
            QMessageBox.information(self, "Comando Enviado", "Comando ativado! Acelere ao máximo.")

    def update_telemetry_loop(self):
        t = self.telemetry
        
        delta_rpm = random.randint(-80, 80)
        delta_volt = random.uniform(-0.3, 0.3)
        delta_curr = random.uniform(-5.0, 5.0)
        delta_temp = random.randint(0, 1) if random.random() > 0.9 else 0
        delta_temp_ctrl = random.randint(0, 1) if random.random() > 0.85 else 0

        t["rpm"] = max(0, min(LIMIT_RPM, t["rpm"] + delta_rpm))
        t["volt"] = max(42.0, min(MAX_VOLT, t["volt"] + delta_volt))
        t["curr"] = max(0.0, min(LIMIT_LINE_CURR, t["curr"] + delta_curr))
        t["temp_motor"] = max(20, min(120, t["temp_motor"] + delta_temp))
        t["temp_mosfet"] = max(20, min(100, t["temp_mosfet"] + delta_temp_ctrl))
        t["throttle"] = random.uniform(1.2, 4.2) if t["curr"] > 10 else random.uniform(0.8, 0.9)
        t["power"] = t["volt"] * t["curr"]
        
        t["hall_a"] = random.choice([True, False])
        t["hall_b"] = random.choice([True, False])
        t["hall_c"] = random.choice([True, False])

        self.card_rpm.update_data(t["rpm"], t["rpm"] - self.prev_telemetry["rpm"])
        self.card_volt.update_data(t["volt"], t["volt"] - self.prev_telemetry["volt"])
        self.card_curr.update_data(t["curr"], t["curr"] - self.prev_telemetry["curr"], reverse_color=True)
        self.card_power.update_data(t["power"], t["power"] - self.prev_telemetry["power"], reverse_color=True)
        self.card_temp.update_data(t["temp_motor"], t["temp_motor"] - self.prev_telemetry["temp_motor"], reverse_color=True)
        self.card_temp_ctrl.update_data(t["temp_mosfet"], t["temp_mosfet"] - self.prev_telemetry["temp_mosfet"], reverse_color=True)
        self.card_throttle.update_data(t["throttle"], t["throttle"] - self.prev_telemetry["throttle"])

        self.hall_widget.update_state(t["hall_a"], t["hall_b"], t["hall_c"])

        self.prev_telemetry = t.copy()

        self.hist_rpm.append(t["rpm"])
        self.hist_curr.append(t["curr"])
        self.hist_volt.append(t["volt"])

        self.line_rpm.setData(list(self.x_data), list(self.hist_rpm))
        self.line_curr.setData(list(self.x_data), list(self.hist_curr))
        self.line_volt.setData(list(self.x_data), list(self.hist_volt))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FardriverApp()
    window.show()
    sys.exit(app.exec_())