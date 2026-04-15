import sys
import os
import webbrowser
from datetime import datetime
from collections import deque
import serial.tools.list_ports

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QSlider, QFrame, QMessageBox, QScrollArea, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

import pyqtgraph as pg

def resource_path(relative_path):
    """ Descobre o caminho absoluto, funcione o código normal ou como .exe """
    try:
        # O PyInstaller cria uma pasta temporária _MEIPASS e guarda o caminho nela
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Importa os nossos módulos personalizados
from fardriver_serial import FardriverSerial
from heb_parser import HebParser
from report_generator import ReportGenerator

STYLESHEET = """
QMainWindow { background-color: #0E1117; }
QLabel { color: #FAFAFA; font-family: "Segoe UI", Arial, sans-serif; }
QFrame#Sidebar { background-color: #262730; border-right: 1px solid #333333; }
QPushButton { background-color: #262730; color: white; border: 1px solid #4B4C52; padding: 8px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { border: 1px solid #FF4B4B; color: #FF4B4B; }
QPushButton:disabled { background-color: #1a1b20; color: #555555; border: 1px solid #333333; }
QPushButton#BtnLigar:hover { border: 1px solid #00FF00; color: #00FF00; }
QPushButton#BtnHeb { background-color: #005580; border: 1px solid #00AAFF; }
QPushButton#BtnHeb:hover { background-color: #00AAFF; color: black; }
QPushButton#BtnFactoryReset { background-color: #8B0000; color: white; border: 1px solid #FF0000; }
QPushButton#BtnFactoryReset:hover { background-color: #FF0000; border: 1px solid #FF6666; }
QPushButton#BtnRelatorio { background-color: #198754; color: white; border: 1px solid #146c43; }
QPushButton#BtnRelatorio:hover { background-color: #157347; border: 1px solid #0a3622; }
QComboBox { background-color: #262730; color: white; border: 1px solid #4B4C52; padding: 5px; border-radius: 4px; }
QComboBox:disabled { background-color: #1a1b20; color: #555555; border: 1px solid #333333; }
QSlider::groove:horizontal { border: 1px solid #4B4C52; height: 4px; background: #4B4C52; border-radius: 2px; }
QSlider::handle:horizontal { background: #FF4B4B; border: 1px solid #FF4B4B; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; }
QSlider::sub-page:horizontal { background: #FF4B4B; border-radius: 2px; }
QSlider::groove:horizontal:disabled { background: #333333; border: 1px solid #333333; }
QSlider::handle:horizontal:disabled { background: #555555; border: 1px solid #555555; }
QSlider::sub-page:horizontal:disabled { background: #555555; }
QScrollArea { border: none; background-color: transparent; }
QFrame#ScrollContent { background-color: transparent; }
QScrollBar:vertical { border: none; background: #262730; width: 8px; }
QScrollBar::handle:vertical { background: #4B4C52; border-radius: 4px; }

/* CORREÇÃO DAS JANELAS DE AVISO */
QMessageBox { background-color: #262730; }
QMessageBox QLabel { color: #FAFAFA; background-color: transparent; }
QMessageBox QPushButton { background-color: #0E1117; color: white; border: 1px solid #4B4C52; min-width: 80px; padding: 5px; }
QMessageBox QPushButton:hover { border: 1px solid #00AAFF; color: #00AAFF; }
"""

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
        self.lbl_value.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.lbl_delta = QLabel(" ")
        self.lbl_delta.setFont(QFont("Segoe UI", 9, QFont.Bold))
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
            
        is_pos = delta_val > 0
        seta = "↑" if is_pos else "↓"
        self.lbl_delta.setText(f"{seta} {abs(delta_val):.1f} {self.unit}")
        
        if (is_pos and not reverse_color) or (not is_pos and reverse_color):
            self.lbl_delta.setStyleSheet("color: #00FF00; background-color: rgba(0, 255, 0, 0.1); padding: 2px; border-radius: 3px;")
        else:
            self.lbl_delta.setStyleSheet("color: #FF4B4B; background-color: rgba(255, 75, 75, 0.1); padding: 2px; border-radius: 3px;")

class HallSensorsWidget(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        lbl = QLabel("Hall:")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl.setStyleSheet("color: #A0A0A0;")
        layout.addWidget(lbl)
        self.leds = [QLabel(c) for c in ("A", "B", "C")]
        for led in self.leds:
            led.setFixedSize(26, 26)
            led.setAlignment(Qt.AlignCenter)
            led.setFont(QFont("Segoe UI", 9, QFont.Bold))
            led.setStyleSheet("background-color: #333333; color: white; border-radius: 13px;")
            layout.addWidget(led)
        self.setLayout(layout)

    def update_state(self, ha, hb, hc):
        colors = ["#FFD700" if ha else "#333333", "#00FF00" if hb else "#333333", "#00AAFF" if hc else "#333333"]
        for i, color in enumerate(colors):
            txt = "black" if color != "#333333" else "white"
            self.leds[i].setStyleSheet(f"background-color: {color}; color: {txt}; border-radius: 13px;")

class FardriverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro - Painel de Telemetria")
        self.resize(1240, 800)
        self.setStyleSheet(STYLESHEET)
        
        self.backend = FardriverSerial()
        self.prev_telemetry = self.backend.telemetry.copy()
        
       # Memória para a TELA (Janela deslizante de 100 pontos)
        self.max_pts_tela = 100 
        
        # Memória FULL para o RELATÓRIO (Listas infinitas)
        self.hist_rpm_full = []
        self.hist_curr_full = []
        self.hist_volt_full = []
        self.hist_temp_motor_full = []
        self.hist_temp_ctrl_full = []
        self._setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_loop)

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # --- SIDEBAR ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(330)
        side_main_layout = QVBoxLayout(sidebar)
        side_main_layout.setContentsMargins(0,0,0,0)
        
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20,20,20,10)
        
        # --- LOGOTIPO DO LEVIATÃ ---
        logo_layout = QHBoxLayout()
        lbl_logo_img = QLabel()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Usa a função mágica para achar a logo dentro do .exe
        logo_path = resource_path("logo.png")
        
        pixmap = QPixmap(logo_path) 
        if not pixmap.isNull():
            lbl_logo_img.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_layout.addWidget(lbl_logo_img)
            
        lbl_titulo = QLabel("Fardriver Pro", font=QFont("Segoe UI", 16, QFont.Bold))
        logo_layout.addWidget(lbl_titulo)
        logo_layout.addStretch() 
        
        header_layout.addLayout(logo_layout)
        header_layout.addWidget(QLabel("Interface Desacoplada (MVC)", font=QFont("Segoe UI", 10)))
        header_layout.addSpacing(10)
        
        self.btn_load_heb = QPushButton("📂 Carregar Backup (.HEB)")
        self.btn_load_heb.setObjectName("BtnHeb")
        self.btn_load_heb.clicked.connect(self.carregar_ficheiro_heb)
        header_layout.addWidget(self.btn_load_heb)
        
        # --- NOVO BOTÃO DE RELATÓRIO WEB ---
        self.btn_relatorio = QPushButton("📄 Gerar Relatório Web")
        self.btn_relatorio.setObjectName("BtnRelatorio")
        self.btn_relatorio.clicked.connect(self.gerar_relatorio_html)
        header_layout.addWidget(self.btn_relatorio)
        # -----------------------------------

        # --- CAIXA COM SELETOR DE PORTAS E BOTÃO REFRESH ---
        box_portas = QHBoxLayout()
        self.cb_portas = QComboBox()
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedWidth(35)
        self.btn_refresh.setToolTip("Procurar portas USB novamente")
        self.btn_refresh.clicked.connect(self.atualizar_lista_portas)
        
        box_portas.addWidget(self.cb_portas)
        box_portas.addWidget(self.btn_refresh)
        header_layout.addLayout(box_portas)
        
        self.atualizar_lista_portas()
        
        self.btn_ligar = QPushButton("Ligar / Desligar")
        self.btn_ligar.setObjectName("BtnLigar")
        self.btn_ligar.clicked.connect(self.toggle_conexao)
        header_layout.addWidget(self.btn_ligar)
        
        self.lbl_status = QLabel("Desligado")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;")
        header_layout.addWidget(self.lbl_status)
        side_main_layout.addWidget(header_frame)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color: #4B4C52; margin: 0px 20px;")
        side_main_layout.addWidget(div)

        # --- ZONA DE SCROLL (CONFIGURAÇÕES) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        scroll_content = QFrame()
        scroll_content.setObjectName("ScrollContent")
        scroll_content.setStyleSheet("background-color: transparent;")
        
        side_layout = QVBoxLayout(scroll_content)
        side_layout.setContentsMargins(20,10,20,20)
        side_layout.setSpacing(15)
        
        row_lock = QHBoxLayout()
        row_lock.addWidget(QLabel("Configurações", font=QFont("Segoe UI", 11, QFont.Bold)))
        self.btn_lock = QPushButton("🔒 Desbloq.")
        self.btn_lock.setFixedWidth(95)
        self.btn_lock.clicked.connect(self.toggle_lock)
        row_lock.addWidget(self.btn_lock)
        side_layout.addLayout(row_lock)

        self.widgets_config = []
        def add_slider(label, min_v, max_v, default):
            lbl_row = QHBoxLayout()
            lbl_row.addWidget(QLabel(label))
            val_lbl = QLabel(str(default))
            val_lbl.setStyleSheet("color: #FF4B4B; font-weight: bold;")
            lbl_row.addWidget(val_lbl, alignment=Qt.AlignRight)
            side_layout.addLayout(lbl_row)
            sl = QSlider(Qt.Horizontal)
            sl.setRange(min_v, max_v)
            sl.setValue(default)
            sl.setEnabled(False)
            sl.valueChanged.connect(lambda v: val_lbl.setText(str(v)))
            side_layout.addWidget(sl)
            self.widgets_config.append(sl)
            return sl

        self.sl_linha = add_slider("Corrente Bateria (A)", 0, self.backend.LIMIT_LINE_CURR, 80)
        self.sl_fase = add_slider("Corrente Fase (A)", 0, self.backend.LIMIT_PHASE_CURR, 250)
        self.sl_regen = add_slider("Freio Regen (A)", 0, 150, 30)
        self.sl_polos = add_slider("Pares de Polos", 1, 40, 4)

        side_layout.addWidget(QLabel("Sensores e Resposta"))
        
        lbl_weaka = QLabel("Enfraquecimento (WeakA):")
        side_layout.addWidget(lbl_weaka)
        self.cb_weaka = QComboBox()
        self.cb_weaka.addItems(["Nível 0 (Desligado)", "Nível 1", "Nível 2", "Nível 3 (Máximo)"])
        self.cb_weaka.setEnabled(False)
        side_layout.addWidget(self.cb_weaka)

        lbl_throttle = QLabel("Modo Acelerador:")
        side_layout.addWidget(lbl_throttle)
        self.cb_throttle = QComboBox()
        self.cb_throttle.addItems(["Line (Linear)", "Sport (Agressivo)", "ECO (Económico)", "Inválido (3)"])
        self.cb_throttle.setEnabled(False)
        side_layout.addWidget(self.cb_throttle)
        
        lbl_sensor = QLabel("Sensor Temp. Motor:")
        side_layout.addWidget(lbl_sensor)
        self.cb_sensor_temp = QComboBox()
        self.cb_sensor_temp.addItems(["Desativado", "KTY83-122", "KTY84-130", "KTY84-150", "PT1000", "NTC10K"])
        self.cb_sensor_temp.setCurrentText("KTY84-130")
        self.cb_sensor_temp.setEnabled(False)
        side_layout.addWidget(self.cb_sensor_temp)

        self.btn_gravar = QPushButton("⬇ Gravar na Controladora")
        self.btn_gravar.setEnabled(False)
        self.btn_gravar.clicked.connect(self.gravar_parametros)
        side_layout.addWidget(self.btn_gravar)
        
        self.btn_autolearn = QPushButton("⚙️ Auto-Aprendizado")
        self.btn_autolearn.setEnabled(False)
        self.btn_autolearn.clicked.connect(self.iniciar_autolearn)
        side_layout.addWidget(self.btn_autolearn)
        
        self.btn_factory_reset = QPushButton("⚠️ Restaurar de Fábrica")
        self.btn_factory_reset.setObjectName("BtnFactoryReset")
        self.btn_factory_reset.setEnabled(False)
        self.btn_factory_reset.clicked.connect(self.restaurar_fabrica)
        side_layout.addWidget(self.btn_factory_reset)

        self.widgets_config.extend([self.cb_weaka, self.cb_throttle, self.cb_sensor_temp, self.btn_gravar, self.btn_autolearn, self.btn_factory_reset])
        side_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        side_main_layout.addWidget(scroll_area)
        main_layout.addWidget(sidebar)

        # --- ÁREA PRINCIPAL ---
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30,30,30,30)
        content_layout.setSpacing(20)
        
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(QLabel("⚡ Painel de Telemetria Fardriver", font=QFont("Segoe UI", 24, QFont.Bold)))
        title_box.addWidget(QLabel("Monitorização Desacoplada com Backend Independente", styleSheet="color: #A0A0A0;"))
        header.addLayout(title_box)
        header.addStretch()
        
        self.hall_widget = HallSensorsWidget()
        header.addWidget(self.hall_widget, alignment=Qt.AlignTop)
        
        self.lbl_erro = QLabel("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.addWidget(self.lbl_erro, alignment=Qt.AlignTop)
        content_layout.addLayout(header)

        m_top = QHBoxLayout()
        self.card_rpm = MetricCard("Rotação", "RPM")
        self.card_volt = MetricCard("Tensão", "V")
        self.card_curr = MetricCard("Corrente", "A")
        self.card_power = MetricCard("Potência", "W")
        for c in (self.card_rpm, self.card_volt, self.card_curr, self.card_power): 
            m_top.addWidget(c)
        content_layout.addLayout(m_top)
        
        m_bot = QHBoxLayout()
        self.card_torque = MetricCard("Binário (Eixo)", "N.m")
        self.card_temp = MetricCard("Temp Motor", "°C")
        self.card_temp_ctrl = MetricCard("Temp Controladora", "°C")
        self.card_throttle = MetricCard("Acelerador", "V")
        for c in (self.card_torque, self.card_temp, self.card_temp_ctrl, self.card_throttle): 
            m_bot.addWidget(c)
        content_layout.addLayout(m_bot)

        lbl_graf = QLabel("Análise de Desempenho Real-Time", font=QFont("Segoe UI", 16, QFont.Bold))
        content_layout.addWidget(lbl_graf)
        
        charts = QHBoxLayout()
        pg.setConfigOption('background', '#0E1117')
        pg.setConfigOption('foreground', '#A0A0A0')
        
        self.p_volt = pg.PlotWidget(title="Tensão (V)")
        self.p_volt.setYRange(40, 60)
        self.l_volt = self.p_volt.plot(pen=pg.mkPen('#00AAFF', width=2))
        
        self.p_curr = pg.PlotWidget(title="Corrente (A)")
        self.p_curr.setYRange(-5, 150)
        self.l_curr = self.p_curr.plot(pen=pg.mkPen('#FF4B4B', width=2))
        
        self.p_rpm = pg.PlotWidget(title="Rotação (RPM)")
        self.p_rpm.setYRange(0, 4500)
        self.l_rpm = self.p_rpm.plot(pen=pg.mkPen('#00FF00', width=2))
        
        for p in (self.p_volt, self.p_curr, self.p_rpm): 
            p.showGrid(y=True, alpha=0.2)
            p.getAxis('bottom').setStyle(showValues=False)
            charts.addWidget(p)
            
        content_layout.addLayout(charts)
        main_layout.addWidget(content)

    def atualizar_lista_portas(self):
        self.cb_portas.clear()
        try:
            portas_disponiveis = [port.device for port in serial.tools.list_ports.comports()]
            if not portas_disponiveis:
                self.cb_portas.addItems(["Nenhuma porta detetada"])
                self.cb_portas.setEnabled(False)
            else:
                self.cb_portas.addItems(portas_disponiveis)
                self.cb_portas.setEnabled(True)
        except Exception as e:
            self.cb_portas.addItems(["Erro de permissão"])
            self.cb_portas.setEnabled(False)

    def carregar_ficheiro_heb(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(self, "Selecionar Backup Fardriver", "", "Ficheiros Fardriver (*.heb);;Todos os Ficheiros (*)", options=options)
        
        if filepath:
            try:
                dados_extraidos = HebParser.parse_file(filepath)
                self.sl_polos.setValue(dados_extraidos["pole_pairs"])
                self.sl_linha.setValue(int(dados_extraidos["line_curr"]))
                self.sl_fase.setValue(int(dados_extraidos["phase_curr"]))
                self.cb_throttle.setCurrentIndex(dados_extraidos["throttle_mode"])
                self.cb_weaka.setCurrentIndex(dados_extraidos["weaka_level"])
                QMessageBox.information(self, "Leitura Concluída", "SUCESSO! Ficheiro lido.\nVerifique os campos à esquerda.")
            except Exception as e:
                QMessageBox.critical(self, "Erro Fatal", f"Ocorreu um erro ao processar o ficheiro:\n{str(e)}")

    def toggle_lock(self):
        is_locked = "Desbloq" in self.btn_lock.text()
        self.btn_lock.setText("🔓 Bloquear" if is_locked else "🔒 Desbloq.")
        self.btn_lock.setStyleSheet("color: #FF4B4B; border: 1px solid #FF4B4B;" if is_locked else "")
        for w in self.widgets_config: 
            w.setEnabled(is_locked)

    def toggle_conexao(self):
        if not self.backend.conectado:
            porta_selecionada = self.cb_portas.currentText()
            if "Nenhuma" in porta_selecionada or "Erro" in porta_selecionada:
                QMessageBox.warning(self, "Aviso", "Ligue o cabo USB da controladora primeiro!")
                return
            sucesso, mensagem_erro = self.backend.conectar(porta_selecionada)
            if sucesso:
                self.lbl_status.setText("ONLINE")
                self.lbl_status.setStyleSheet("background-color: rgba(0, 255, 0, 0.1); color: #00FF00; padding: 10px; font-weight: bold;")
                self.lbl_erro.setText("SISTEMA OK")
                self.lbl_erro.setStyleSheet("color: #00FF00;")
                self.btn_ligar.setText("Desligar")
                self.timer.start(100)
            else:
                QMessageBox.critical(self, "Falha na Comunicação USB", f"Não foi possível abrir a porta.\n\n{mensagem_erro}")
        else:
            self.backend.desconectar()
            self.lbl_status.setText("DESLIGADO")
            self.lbl_status.setStyleSheet("background-color: #262730; color: #FF4B4B; padding: 10px;")
            self.lbl_erro.setText("AGUARDAR LIGAÇÃO...")
            self.lbl_erro.setStyleSheet("color: #A0A0A0;")
            self.btn_ligar.setText("Ligar / Desligar")
            self.timer.stop()
            self.hall_widget.update_state(0,0,0)
            self.hist_rpm.clear()
            self.hist_curr.clear()
            self.hist_volt.clear()

    def gravar_parametros(self):
        cfg = {
            "linha_a": self.sl_linha.value(),
            "fase_a": self.sl_fase.value(),
            "polos": self.sl_polos.value(),
            "weaka": self.cb_weaka.currentIndex(),
            "throttle": self.cb_throttle.currentIndex()
        }
        if self.backend.enviar_configuracoes(cfg):
            QMessageBox.information(self, "Sucesso", "Parâmetros enviados para a controladora.")
        else:
            QMessageBox.warning(self, "Erro", "Ligue primeiro o dispositivo!")

    def iniciar_autolearn(self):
        if self.backend.iniciar_autolearn():
            QMessageBox.information(self, "Comando Enviado", "Comando ativado! Acelere ao máximo.")
        else:
            QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def restaurar_fabrica(self):
        resposta = QMessageBox.question(self, "ALERTA CRÍTICO - RESTAURAR DE FÁBRICA", 
            "⚠️ ATENÇÃO: Deseja prosseguir com o Factory Reset?", QMessageBox.Yes | QMessageBox.No)
        if resposta == QMessageBox.Yes:
            if self.backend.restaurar_fabrica():
                QMessageBox.information(self, "Restauro Concluído", "Controladora restaurada.")
            else:
                QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def update_telemetry_loop(self):
        t = self.backend.ler_dados()

        self.card_rpm.update_data(t["rpm"], t["rpm"] - self.prev_telemetry["rpm"])
        self.card_volt.update_data(t["volt"], t["volt"] - self.prev_telemetry["volt"])
        self.card_curr.update_data(t["curr"], t["curr"] - self.prev_telemetry["curr"], True)
        self.card_power.update_data(t["power"], t["power"] - self.prev_telemetry["power"], True)
        self.card_torque.update_data(t["torque"], t["torque"] - self.prev_telemetry["torque"], True)
        self.card_temp.update_data(t["temp_motor"], 0, True)
        self.card_temp_ctrl.update_data(t["temp_mosfet"], 0, True)
        self.card_throttle.update_data(t["throttle"], 0)
        
        self.hall_widget.update_state(t["hall_a"], t["hall_b"], t["hall_c"])

        self.prev_telemetry = t.copy()
        
        # --- 1. GUARDA TUDO NA MEMÓRIA FULL (Para o Relatório) ---
        self.hist_rpm_full.append(t["rpm"])
        self.hist_curr_full.append(t["curr"])
        self.hist_volt_full.append(t["volt"])
        self.hist_temp_motor_full.append(t["temp_motor"])
        self.hist_temp_ctrl_full.append(t["temp_mosfet"])
        
        # --- 2. ATUALIZA A TELA (Apenas os últimos 100 pontos para não travar) ---
        eixo_x_completo = list(range(len(self.hist_rpm_full)))
        
        self.l_rpm.setData(eixo_x_completo[-self.max_pts_tela:], self.hist_rpm_full[-self.max_pts_tela:])
        self.l_curr.setData(eixo_x_completo[-self.max_pts_tela:], self.hist_curr_full[-self.max_pts_tela:])
        self.l_volt.setData(eixo_x_completo[-self.max_pts_tela:], self.hist_volt_full[-self.max_pts_tela:])

    # =========================================================================
    # GERADOR DE RELATÓRIO HTML OFFLINE
    # =========================================================================
    # =========================================================================
    # GERADOR DE RELATÓRIO HTML OFFLINE
    # =========================================================================
    def gerar_relatorio_html(self):
        # --- TRAVA DE SEGURANÇA: Evita erro se não houver dados ---
        if not self.hist_rpm_full:
            QMessageBox.warning(self, "Sem Dados", "Não há dados para exportar! Ligue a controladora e aguarde a leitura do gráfico.")
            return
        # ----------------------------------------------------------

        t = self.backend.ler_dados()
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        
        caminho_salvar, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Relatório de Teste", 
            f"Relatorio_Leviata_{datetime.now().strftime('%Y%m%d_%H%M')}.html", 
            "Arquivos Web (*.html)", 
            options=options
        )
        
        if not caminho_salvar:
            return
            
        pasta_escolhida = os.path.dirname(caminho_salvar)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        from report_generator import ReportGenerator
        ReportGenerator.generate_html_report(
            t, 
            self.hist_rpm_full, 
            self.hist_curr_full, 
            self.hist_volt_full, 
            list(range(len(self.hist_rpm_full))), 
            pasta_escolhida,
            self.hist_temp_motor_full,  
            self.hist_temp_ctrl_full    
        )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FardriverApp()
    window.show()
    sys.exit(app.exec_())