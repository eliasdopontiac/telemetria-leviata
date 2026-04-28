import csv
import json
import os
import sys
import webbrowser
from collections import deque
from datetime import datetime

import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


def resource_path(relative_path):
    """Descobre o caminho absoluto, funcione o código normal ou como .exe"""
    try:
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
QPushButton#BtnCSV { background-color: #155a8a; color: white; border: 1px solid #1a7fc4; }
QPushButton#BtnCSV:hover { background-color: #1a7fc4; color: white; }
QPushButton#BtnSavePerfil { background-color: #2d5a27; color: white; border: 1px solid #3d7a35; }
QPushButton#BtnSavePerfil:hover { background-color: #3d7a35; color: white; }
QPushButton#BtnLoadPerfil { background-color: #4a3800; color: white; border: 1px solid #7a5c00; }
QPushButton#BtnLoadPerfil:hover { background-color: #7a5c00; color: white; }
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

/* ABAS */
QTabWidget::pane { border: 1px solid #333; background-color: #0E1117; }
QTabBar::tab { background: #262730; color: #A0A0A0; padding: 8px 16px; border: 1px solid #333; }
QTabBar::tab:selected { background: #0E1117; color: #FAFAFA; border-bottom: 2px solid #FF4B4B; }

/* GROUPBOX */
QGroupBox { color: #A0A0A0; border: 1px solid #333; margin-top: 8px; padding-top: 8px; border-radius: 4px; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #FF4B4B; font-weight: bold; }

/* SPINBOXES */
QSpinBox, QDoubleSpinBox { background-color: #262730; color: white; border: 1px solid #4B4C52; padding: 4px; border-radius: 4px; }
QSpinBox:disabled, QDoubleSpinBox:disabled { background-color: #1a1b20; color: #555555; }
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button { background-color: #333; border: none; }

/* TABELA */
QTableWidget { background-color: #0E1117; color: white; gridline-color: #333; }
QTableWidget::item:selected { background-color: #FF4B4B; }
QHeaderView::section { background-color: #262730; color: #A0A0A0; padding: 4px; border: 1px solid #333; }

/* LIST WIDGET */
QListWidget { background-color: #0E1117; color: white; border: 1px solid #333; }
"""

# Perfis de PID pré-definidos
PID_PROFILES = {
    "Motor Pequena Potência": {
        "StartKI": 8,
        "MidKI": 8,
        "MaxKI": 12,
        "StartKP": 80,
        "MidKP": 80,
        "MaxKP": 120,
    },
    "Potência Média": {
        "StartKI": 6,
        "MidKI": 6,
        "MaxKI": 9,
        "StartKP": 60,
        "MidKP": 60,
        "MaxKP": 90,
    },
    "Alta Potência": {
        "StartKI": 4,
        "MidKI": 4,
        "MaxKI": 6,
        "StartKP": 40,
        "MidKP": 40,
        "MaxKP": 60,
    },
    "Ultra Alta Potência": {
        "StartKI": 2,
        "MidKI": 2,
        "MaxKI": 3,
        "StartKP": 20,
        "MidKP": 20,
        "MaxKP": 30,
    },
    "Personalizado": None,
}

RPM_LABELS = [
    "Min",
    "500",
    "1000",
    "1500",
    "2000",
    "2500",
    "3000",
    "3500",
    "4000",
    "4500",
    "5000",
    "5500",
    "6000",
    "6500",
    "7000",
    "7500",
    "8000",
    "Max",
]


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
            self.lbl_delta.setStyleSheet(
                "color: #00FF00; background-color: rgba(0, 255, 0, 0.1); padding: 2px; border-radius: 3px;"
            )
        else:
            self.lbl_delta.setStyleSheet(
                "color: #FF4B4B; background-color: rgba(255, 75, 75, 0.1); padding: 2px; border-radius: 3px;"
            )


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
            led.setStyleSheet(
                "background-color: #333333; color: white; border-radius: 13px;"
            )
            layout.addWidget(led)
        self.setLayout(layout)

    def update_state(self, ha, hb, hc):
        colors = [
            "#FFD700" if ha else "#333333",
            "#00FF00" if hb else "#333333",
            "#00AAFF" if hc else "#333333",
        ]
        for i, color in enumerate(colors):
            txt = "black" if color != "#333333" else "white"
            self.leds[i].setStyleSheet(
                f"background-color: {color}; color: {txt}; border-radius: 13px;"
            )


class FardriverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro — Bancada de Testes · Leviatã UEA")
        self.resize(1280, 860)
        self.setStyleSheet(STYLESHEET)

        self.backend = FardriverSerial()
        self.prev_telemetry = self.backend.ler_dados()

        # Memória para a TELA (Janela deslizante de 100 pontos)
        self.max_pts_tela = 100

        # Memória FULL para o RELATÓRIO (Listas infinitas)
        self.hist_rpm_full = []
        self.hist_curr_full = []
        self.hist_volt_full = []
        self.hist_temp_motor_full = []
        self.hist_temp_ctrl_full = []
        self.hist_torque_full = []
        self.hist_throttle_full = []
        self.hist_error_full = []
        self.hist_soc_full = []
        self._tick = 0

        # Dicionário de referência para os spinboxes de parâmetros
        self.params_widgets = {}

        self._setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_loop)

        # Watchdog: callback do backend quando o cabo é desconectado
        if hasattr(self.backend, "on_disconnect_callback"):
            self.backend.on_disconnect_callback = self._on_watchdog_disconnect

    # =========================================================================
    # SETUP DA INTERFACE
    # =========================================================================
    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------------------------------------------------------ #
        #  SIDEBAR                                                             #
        # ------------------------------------------------------------------ #
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(330)
        side_main_layout = QVBoxLayout(sidebar)
        side_main_layout.setContentsMargins(0, 0, 0, 0)

        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 10)

        # Logo
        logo_layout = QHBoxLayout()
        lbl_logo_img = QLabel()
        logo_path = resource_path("logo.png")
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            lbl_logo_img.setPixmap(
                pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            logo_layout.addWidget(lbl_logo_img)
        lbl_titulo = QLabel("Fardriver Pro", font=QFont("Segoe UI", 16, QFont.Bold))
        logo_layout.addWidget(lbl_titulo)
        logo_layout.addStretch()
        header_layout.addLayout(logo_layout)
        header_layout.addWidget(
            QLabel("Interface Desacoplada (MVC)", font=QFont("Segoe UI", 10))
        )
        header_layout.addSpacing(10)

        self.btn_load_heb = QPushButton("📂 Carregar Backup (.HEB)")
        self.btn_load_heb.setObjectName("BtnHeb")
        self.btn_load_heb.clicked.connect(self.carregar_ficheiro_heb)
        header_layout.addWidget(self.btn_load_heb)

        self.btn_relatorio = QPushButton("📄 Gerar Relatório Web")
        self.btn_relatorio.setObjectName("BtnRelatorio")
        self.btn_relatorio.clicked.connect(self.gerar_relatorio_html)
        header_layout.addWidget(self.btn_relatorio)

        self.btn_exportar_csv = QPushButton("📊 Exportar CSV")
        self.btn_exportar_csv.setObjectName("BtnCSV")
        self.btn_exportar_csv.clicked.connect(self.exportar_csv)
        header_layout.addWidget(self.btn_exportar_csv)

        perfil_row = QHBoxLayout()
        self.btn_salvar_perfil = QPushButton("💾 Salvar Perfil")
        self.btn_salvar_perfil.setObjectName("BtnSavePerfil")
        self.btn_salvar_perfil.clicked.connect(self.salvar_perfil)
        self.btn_carregar_perfil = QPushButton("📂 Carregar Perfil")
        self.btn_carregar_perfil.setObjectName("BtnLoadPerfil")
        self.btn_carregar_perfil.clicked.connect(self.carregar_perfil)
        perfil_row.addWidget(self.btn_salvar_perfil)
        perfil_row.addWidget(self.btn_carregar_perfil)
        header_layout.addLayout(perfil_row)

        # Portas
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
        self.lbl_status.setStyleSheet(
            "background-color: #262730; color: #FF4B4B; padding: 10px; border-radius: 4px;"
        )
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
        side_layout.setContentsMargins(20, 10, 20, 20)
        side_layout.setSpacing(15)

        row_lock = QHBoxLayout()
        row_lock.addWidget(
            QLabel("Configurações", font=QFont("Segoe UI", 11, QFont.Bold))
        )
        self.btn_lock = QPushButton("🔒 Desbloquear")
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

        self.sl_linha = add_slider(
            "Corrente Linha / Bateria (A)", 0, self.backend.LIMIT_LINE_CURR, 80
        )
        self.sl_fase = add_slider(
            "Corrente Fase / Motor (A)", 0, self.backend.LIMIT_PHASE_CURR, 250
        )
        self.sl_regen = add_slider("Frenagem Regenerativa (A)", 0, 150, 30)
        self.sl_polos = add_slider("Pares de Polos", 1, 40, 4)

        side_layout.addWidget(QLabel("Sensores e Resposta"))

        lbl_weaka = QLabel("Campo Fraco (Weak Field):")
        side_layout.addWidget(lbl_weaka)
        self.cb_weaka = QComboBox()
        self.cb_weaka.addItems(
            ["Nível 0 (Desligado)", "Nível 1", "Nível 2", "Nível 3 (Máximo)"]
        )
        self.cb_weaka.setEnabled(False)
        side_layout.addWidget(self.cb_weaka)

        lbl_throttle = QLabel("Resposta do Acelerador:")
        side_layout.addWidget(lbl_throttle)
        self.cb_throttle = QComboBox()
        self.cb_throttle.addItems(
            ["Linear (Padrão)", "Sport (Agressivo)", "ECO (Econômico)", "Inválido (3)"]
        )
        self.cb_throttle.setEnabled(False)
        side_layout.addWidget(self.cb_throttle)

        lbl_sensor = QLabel("Sensor Temp. Motor:")
        side_layout.addWidget(lbl_sensor)
        self.cb_sensor_temp = QComboBox()
        self.cb_sensor_temp.addItems(
            ["Desativado", "KTY83-122", "KTY84-130", "KTY84-150", "PT1000", "NTC10K"]
        )
        self.cb_sensor_temp.setCurrentText("KTY84-130")
        self.cb_sensor_temp.setEnabled(False)
        side_layout.addWidget(self.cb_sensor_temp)

        self.btn_gravar = QPushButton("💾 Gravar na Controladora")
        self.btn_gravar.setEnabled(False)
        self.btn_gravar.clicked.connect(self.gravar_parametros)
        side_layout.addWidget(self.btn_gravar)

        autolearn_row = QHBoxLayout()
        self.btn_autolearn = QPushButton("⚙️ Auto-Aprendizado")
        self.btn_autolearn.setEnabled(False)
        self.btn_autolearn.clicked.connect(self.iniciar_autolearn)
        self.btn_cancel_autolearn = QPushButton("✖ Cancelar Learn")
        self.btn_cancel_autolearn.setEnabled(False)
        self.btn_cancel_autolearn.setToolTip("Cancela o Auto-Aprendizado em andamento")
        self.btn_cancel_autolearn.setStyleSheet(
            "QPushButton { color: #FFA500; border: 1px solid #FFA500; }"
            "QPushButton:hover { background-color: #FFA500; color: black; }"
            "QPushButton:disabled { color: #555555; border: 1px solid #333333; }"
        )
        self.btn_cancel_autolearn.clicked.connect(self.cancelar_autolearn)
        autolearn_row.addWidget(self.btn_autolearn)
        autolearn_row.addWidget(self.btn_cancel_autolearn)
        side_layout.addLayout(autolearn_row)

        self.btn_factory_reset = QPushButton("⚠️ Restaurar de Fábrica")
        self.btn_factory_reset.setObjectName("BtnFactoryReset")
        self.btn_factory_reset.setEnabled(False)
        self.btn_factory_reset.clicked.connect(self.restaurar_fabrica)
        side_layout.addWidget(self.btn_factory_reset)

        self.widgets_config.extend(
            [
                self.cb_weaka,
                self.cb_throttle,
                self.cb_sensor_temp,
                self.btn_gravar,
                self.btn_autolearn,
                self.btn_cancel_autolearn,
                self.btn_factory_reset,
            ]
        )
        side_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        side_main_layout.addWidget(scroll_area)
        main_layout.addWidget(sidebar)

        # ------------------------------------------------------------------ #
        #  ÁREA PRINCIPAL COM QTabWidget                                       #
        # ------------------------------------------------------------------ #
        content = QFrame()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(10)

        # Cabeçalho principal (fora das abas)
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(
            QLabel(
                "⚡ Painel de Telemetria Fardriver",
                font=QFont("Segoe UI", 22, QFont.Bold),
            )
        )
        title_box.addWidget(
            QLabel(
                "Bancada de Testes — Leviatã UEA",
                styleSheet="color: #A0A0A0;",
            )
        )
        header.addLayout(title_box)
        header.addStretch()

        self.hall_widget = HallSensorsWidget()
        header.addWidget(self.hall_widget, alignment=Qt.AlignTop)

        self.lbl_erro = QLabel("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setFont(QFont("Segoe UI", 12, QFont.Bold))
        header.addWidget(self.lbl_erro, alignment=Qt.AlignTop)
        content_layout.addLayout(header)

        # Indicadores de status
        status_row = QHBoxLayout()
        status_row.setSpacing(16)
        self.lbl_forward = QLabel("▶ MARCHA")
        self.lbl_forward.setStyleSheet(
            "color: #555; font-size: 10px; font-weight: bold;"
        )
        self.lbl_reverse = QLabel("◀ RÉ")
        self.lbl_reverse.setStyleSheet(
            "color: #555; font-size: 10px; font-weight: bold;"
        )
        self.lbl_brake = QLabel("⬛ FREIO")
        self.lbl_brake.setStyleSheet("color: #555; font-size: 10px; font-weight: bold;")
        self.lbl_motion = QLabel("◉ MOVIMENTO")
        self.lbl_motion.setStyleSheet(
            "color: #555; font-size: 10px; font-weight: bold;"
        )
        status_row.addStretch()
        status_row.addWidget(self.lbl_forward)
        status_row.addWidget(self.lbl_reverse)
        status_row.addWidget(self.lbl_brake)
        status_row.addWidget(self.lbl_motion)
        content_layout.addLayout(status_row)

        # Tab Widget
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)

        # Status bar inferior
        status_bar = QFrame()
        status_bar.setStyleSheet("background-color: #262730; border-top: 1px solid #333333;")
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 6, 12, 6)
        status_layout.setSpacing(20)
        
        self.lbl_status_connection = QLabel("Status: Desligado")
        self.lbl_status_connection.setStyleSheet("color: #FF4B4B; font-size: 10px;")
        status_layout.addWidget(self.lbl_status_connection)
        
        self.lbl_status_errors = QLabel("Erros: 0")
        self.lbl_status_errors.setStyleSheet("color: #A0A0A0; font-size: 10px;")
        status_layout.addWidget(self.lbl_status_errors)
        
        self.lbl_status_datarate = QLabel("Taxa: 0 Hz")
        self.lbl_status_datarate.setStyleSheet("color: #A0A0A0; font-size: 10px;")
        status_layout.addWidget(self.lbl_status_datarate)
        
        self.lbl_status_packets = QLabel("Pacotes: 0")
        self.lbl_status_packets.setStyleSheet("color: #A0A0A0; font-size: 10px;")
        status_layout.addWidget(self.lbl_status_packets)
        
        status_layout.addStretch()
        
        self.lbl_status_version = QLabel("Fardriver Pro v2.0")
        self.lbl_status_version.setStyleSheet("color: #666666; font-size: 9px;")
        status_layout.addWidget(self.lbl_status_version)
        
        content_layout.addWidget(status_bar)

        # ------ Aba 1: Dashboard ------
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        dashboard_layout.setContentsMargins(0, 12, 0, 0)
        dashboard_layout.setSpacing(14)

        m_top = QHBoxLayout()
        self.card_rpm = MetricCard("Rotação (Motor)", "RPM")
        self.card_volt = MetricCard("Tensão", "V")
        self.card_curr = MetricCard("Corrente Linha", "A")
        self.card_power = MetricCard("Potência", "W")
        self.card_soc = MetricCard("Bateria (SOC)", "%")
        for c in (
            self.card_rpm,
            self.card_volt,
            self.card_curr,
            self.card_power,
            self.card_soc,
        ):
            m_top.addWidget(c)
        dashboard_layout.addLayout(m_top)

        m_bot = QHBoxLayout()
        self.card_torque = MetricCard("Torque", "N·m")
        self.card_temp = MetricCard("Temp. Motor", "°C")
        self.card_temp_ctrl = MetricCard("Temp. Controladora", "°C")
        self.card_throttle = MetricCard("Acelerador", "V")
        for c in (
            self.card_torque,
            self.card_temp,
            self.card_temp_ctrl,
            self.card_throttle,
        ):
            m_bot.addWidget(c)
        dashboard_layout.addLayout(m_bot)

        lbl_graf = QLabel(
            "Análise de Desempenho Real-Time", font=QFont("Segoe UI", 14, QFont.Bold)
        )
        dashboard_layout.addWidget(lbl_graf)

        charts = QHBoxLayout()
        pg.setConfigOption("background", "#0E1117")
        pg.setConfigOption("foreground", "#A0A0A0")

        self.p_volt = pg.PlotWidget(title="Tensão de Bateria (V)")
        self.p_volt.setYRange(40, 60)
        self.l_volt = self.p_volt.plot(pen=pg.mkPen("#00AAFF", width=2))

        self.p_curr = pg.PlotWidget(title="Corrente Linha (A)")
        self.p_curr.setYRange(-5, 150)
        self.l_curr = self.p_curr.plot(pen=pg.mkPen("#FF4B4B", width=2))

        self.p_rpm = pg.PlotWidget(title="Rotação do Motor (RPM)")
        self.p_rpm.setYRange(0, 4500)
        self.l_rpm = self.p_rpm.plot(pen=pg.mkPen("#00FF00", width=2))

        for p in (self.p_volt, self.p_curr, self.p_rpm):
            p.showGrid(y=True, alpha=0.2)
            p.getAxis("bottom").setStyle(showValues=False)
            charts.addWidget(p)

        dashboard_layout.addLayout(charts)
        self.tab_widget.addTab(dashboard_tab, "📊 Dashboard")

        # ------ Aba 2: Parâmetros ------
        params_tab = self._build_params_tab()
        self.tab_widget.addTab(params_tab, "⚙️ Parâmetros")

        # ------ Aba 3: Coleta de Dados ------
        data_tab = self._build_data_collection_tab()
        self.tab_widget.addTab(data_tab, "📈 Coleta de Dados")

        # ------ Aba 4: Erros ------
        error_tab = self._build_error_log_tab()
        self.tab_widget.addTab(error_tab, "📋 Erros")

        main_layout.addWidget(content)

    # =========================================================================
    # CONSTRUÇÃO DAS ABAS
    # =========================================================================

    def _build_params_tab(self):
        """Cria e retorna o widget da aba de Parâmetros completos."""
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # ---------- Seção: Motor ----------
        grp_motor = QGroupBox("Motor")
        grp_layout = QVBoxLayout(grp_motor)

        def make_row(label_text, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(220)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            grp_layout.addLayout(row)

        sb_rated_speed = QSpinBox()
        sb_rated_speed.setRange(0, 9000)
        sb_rated_speed.setSuffix(" RPM")
        sb_rated_speed.setFixedWidth(130)
        self.params_widgets["rated_speed"] = sb_rated_speed
        make_row("Velocidade Nominal:", sb_rated_speed)

        sb_rated_voltage = QDoubleSpinBox()
        sb_rated_voltage.setRange(24.0, 120.0)
        sb_rated_voltage.setSuffix(" V")
        sb_rated_voltage.setSingleStep(0.5)
        sb_rated_voltage.setFixedWidth(130)
        self.params_widgets["rated_voltage"] = sb_rated_voltage
        make_row("Tensão Nominal:", sb_rated_voltage)

        sb_rated_power = QSpinBox()
        sb_rated_power.setRange(0, 20000)
        sb_rated_power.setSuffix(" W")
        sb_rated_power.setFixedWidth(130)
        self.params_widgets["rated_power"] = sb_rated_power
        make_row("Potência Nominal:", sb_rated_power)

        sb_phase_offset = QDoubleSpinBox()
        sb_phase_offset.setRange(-360.0, 360.0)
        sb_phase_offset.setSuffix(" °")
        sb_phase_offset.setSingleStep(0.5)
        sb_phase_offset.setFixedWidth(130)
        self.params_widgets["phase_offset"] = sb_phase_offset
        make_row("Offset de Fase:", sb_phase_offset)

        cb_direction = QComboBox()
        cb_direction.addItems(["Esquerda (Padrão)", "Direita (Invertido)"])
        cb_direction.setFixedWidth(200)
        self.params_widgets["direction"] = cb_direction
        row_dir = QHBoxLayout()
        lbl_dir = QLabel("Direção:")
        lbl_dir.setFixedWidth(220)
        row_dir.addWidget(lbl_dir)
        row_dir.addWidget(cb_direction)
        row_dir.addStretch()
        grp_layout.addLayout(row_dir)

        layout.addWidget(grp_motor)

        # ---------- Seção: Proteções ----------
        grp_prot = QGroupBox("Proteções")
        grp_prot_layout = QVBoxLayout(grp_prot)

        def make_row_p(label_text, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(220)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            grp_prot_layout.addLayout(row)

        sb_low_vol = QDoubleSpinBox()
        sb_low_vol.setRange(10.0, 100.0)
        sb_low_vol.setSuffix(" V")
        sb_low_vol.setSingleStep(0.5)
        sb_low_vol.setFixedWidth(130)
        self.params_widgets["low_vol_protect"] = sb_low_vol
        make_row_p("Proteção de Baixa Tensão:", sb_low_vol)

        sb_motor_temp = QSpinBox()
        sb_motor_temp.setRange(60, 150)
        sb_motor_temp.setSuffix(" °C")
        sb_motor_temp.setFixedWidth(130)
        self.params_widgets["motor_temp_protect"] = sb_motor_temp
        make_row_p("Proteção Temp. Motor:", sb_motor_temp)

        sb_mos_temp = QSpinBox()
        sb_mos_temp.setRange(60, 120)
        sb_mos_temp.setSuffix(" °C")
        sb_mos_temp.setFixedWidth(130)
        self.params_widgets["mos_temp_protect"] = sb_mos_temp
        make_row_p("Proteção Temp. MOSFET:", sb_mos_temp)

        layout.addWidget(grp_prot)

        # ---------- Seção: Acelerador ----------
        grp_acc = QGroupBox("Acelerador")
        grp_acc_layout = QVBoxLayout(grp_acc)

        def make_row_a(label_text, widget):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(220)
            row.addWidget(lbl)
            row.addWidget(widget)
            row.addStretch()
            grp_acc_layout.addLayout(row)

        sb_thr_low = QDoubleSpinBox()
        sb_thr_low.setRange(0.0, 3.0)
        sb_thr_low.setSuffix(" V")
        sb_thr_low.setSingleStep(0.05)
        sb_thr_low.setFixedWidth(130)
        self.params_widgets["throttle_low"] = sb_thr_low
        make_row_a("Tensão Mínima do Acelerador:", sb_thr_low)

        sb_thr_high = QDoubleSpinBox()
        sb_thr_high.setRange(2.0, 5.0)
        sb_thr_high.setSuffix(" V")
        sb_thr_high.setSingleStep(0.05)
        sb_thr_high.setFixedWidth(130)
        self.params_widgets["throttle_high"] = sb_thr_high
        make_row_a("Tensão Máxima do Acelerador:", sb_thr_high)

        layout.addWidget(grp_acc)

        # ---------- Seção: PID ----------
        grp_pid = QGroupBox("PID")
        grp_pid_layout = QVBoxLayout(grp_pid)

        pid_profile_row = QHBoxLayout()
        lbl_pid_profile = QLabel("Perfil:")
        lbl_pid_profile.setFixedWidth(80)
        self.cb_pid_profile = QComboBox()
        self.cb_pid_profile.addItems(list(PID_PROFILES.keys()))
        self.cb_pid_profile.setFixedWidth(240)
        self.cb_pid_profile.currentTextChanged.connect(self._on_pid_profile_changed)
        pid_profile_row.addWidget(lbl_pid_profile)
        pid_profile_row.addWidget(self.cb_pid_profile)
        pid_profile_row.addStretch()
        grp_pid_layout.addLayout(pid_profile_row)

        pid_fields = [
            ("StartKI", 0, 30),
            ("MidKI", 0, 30),
            ("MaxKI", 0, 30),
            ("StartKP", 0, 255),
            ("MidKP", 0, 255),
            ("MaxKP", 0, 255),
        ]

        pid_grid = QHBoxLayout()
        pid_col1 = QVBoxLayout()
        pid_col2 = QVBoxLayout()

        for idx, (name, mn, mx) in enumerate(pid_fields):
            sb = QSpinBox()
            sb.setRange(mn, mx)
            sb.setFixedWidth(100)
            self.params_widgets[name] = sb
            row = QHBoxLayout()
            lbl = QLabel(f"{name}:")
            lbl.setFixedWidth(80)
            row.addWidget(lbl)
            row.addWidget(sb)
            row.addStretch()
            if idx < 3:
                pid_col1.addLayout(row)
            else:
                pid_col2.addLayout(row)

        pid_grid.addLayout(pid_col1)
        pid_grid.addSpacing(30)
        pid_grid.addLayout(pid_col2)
        pid_grid.addStretch()
        grp_pid_layout.addLayout(pid_grid)
        layout.addWidget(grp_pid)

        # ---------- Seção: Tabela Ratio por RPM ----------
        grp_ratio = QGroupBox("Tabela de Corrente por RPM")
        grp_ratio_layout = QVBoxLayout(grp_ratio)

        self.tbl_ratio = QTableWidget(len(RPM_LABELS), 2)
        self.tbl_ratio.setHorizontalHeaderLabels(["RPM", "Limite (%)"])
        self.tbl_ratio.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_ratio.setMaximumHeight(320)
        for row_idx, rpm_lbl in enumerate(RPM_LABELS):
            rpm_item = QTableWidgetItem(rpm_lbl)
            rpm_item.setFlags(rpm_item.flags() & ~Qt.ItemIsEditable)
            self.tbl_ratio.setItem(row_idx, 0, rpm_item)
            val_item = QTableWidgetItem("100")
            self.tbl_ratio.setItem(row_idx, 1, val_item)
        grp_ratio_layout.addWidget(self.tbl_ratio)
        layout.addWidget(grp_ratio)

        # ---------- Seção: Tabela nRatio por RPM ----------
        grp_nratio = QGroupBox("Tabela Regen por RPM")
        grp_nratio_layout = QVBoxLayout(grp_nratio)

        self.tbl_nratio = QTableWidget(len(RPM_LABELS), 2)
        self.tbl_nratio.setHorizontalHeaderLabels(["RPM", "Limite (%)"])
        self.tbl_nratio.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_nratio.setMaximumHeight(320)
        for row_idx, rpm_lbl in enumerate(RPM_LABELS):
            rpm_item = QTableWidgetItem(rpm_lbl)
            rpm_item.setFlags(rpm_item.flags() & ~Qt.ItemIsEditable)
            self.tbl_nratio.setItem(row_idx, 0, rpm_item)
            val_item = QTableWidgetItem("0")
            self.tbl_nratio.setItem(row_idx, 1, val_item)
        grp_nratio_layout.addWidget(self.tbl_nratio)
        layout.addWidget(grp_nratio)

        # ---------- Botões do rodapé da aba ----------
        btn_row = QHBoxLayout()
        btn_ler = QPushButton("🔄 Ler da Controladora")
        btn_ler.clicked.connect(self._populate_params_from_backend)
        btn_gravar_all = QPushButton("💾 Gravar Tudo")
        btn_gravar_all.clicked.connect(self.gravar_parametros_completos)
        btn_row.addStretch()
        btn_row.addWidget(btn_ler)
        btn_row.addWidget(btn_gravar_all)
        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(inner)
        outer_layout.addWidget(scroll)
        return outer

    def _build_data_collection_tab(self):
        """Cria e retorna o widget da aba de Coleta de Dados."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        btn_iniciar_coleta = QPushButton("▶ Iniciar Coleta (2048 amostras)")
        btn_iniciar_coleta.setFixedWidth(260)
        btn_iniciar_coleta.clicked.connect(self._iniciar_coleta_dados)
        top_row.addWidget(btn_iniciar_coleta)
        top_row.addStretch()
        layout.addLayout(top_row)

        lbl_info = QLabel(
            "Inicia a gravação de 2048 amostras do ciclo de aceleração na flash. "
            "Após iniciar, acelere o motor ao máximo por ~20 segundos."
        )
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        layout.addWidget(lbl_info)

        self.p_coleta = pg.PlotWidget(title="Dados Coletados (2048 amostras)")
        self.p_coleta.showGrid(y=True, alpha=0.2)
        self.p_coleta.setLabel("bottom", "Amostra")
        self.p_coleta.setLabel("left", "Valor")
        layout.addWidget(self.p_coleta, stretch=1)

        btn_exportar_relatorio = QPushButton("📄 Exportar para Relatório")
        btn_exportar_relatorio.setEnabled(False)
        btn_exportar_relatorio.setToolTip("Reservado para uso futuro")
        layout.addWidget(btn_exportar_relatorio, alignment=Qt.AlignRight)

        return widget

    def _build_error_log_tab(self):
        """Cria e retorna o widget da aba de Log de Erros."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        lbl_title = QLabel("Histórico de Erros", font=QFont("Segoe UI", 13, QFont.Bold))
        top_row.addWidget(lbl_title)
        top_row.addStretch()
        btn_limpar = QPushButton("🗑 Limpar Histórico")
        btn_limpar.clicked.connect(self._limpar_historico_erros)
        top_row.addWidget(btn_limpar)
        layout.addLayout(top_row)

        self.lst_erros = QListWidget()
        self.lst_erros.setFont(QFont("Courier New", 10))
        self.lst_erros.setStyleSheet(
            "QListWidget { background-color: #0E1117; color: white; border: 1px solid #333; }"
            "QListWidget::item { padding: 4px; border-bottom: 1px solid #1c1c2a; }"
        )
        layout.addWidget(self.lst_erros)

        return widget

    # =========================================================================
    # LÓGICA DOS PARÂMETROS
    # =========================================================================

    def _on_pid_profile_changed(self, profile_name):
        """Preenche automaticamente os campos de PID ao selecionar um perfil."""
        values = PID_PROFILES.get(profile_name)
        if values is None:
            # Personalizado: não altera os campos
            return
        for key, val in values.items():
            sb = self.params_widgets.get(key)
            if sb is not None:
                sb.setValue(val)

    def populate_params_tab(self, params: dict):
        """Preenche todos os campos da aba de parâmetros com valores do dicionário."""
        for key, widget in self.params_widgets.items():
            if key not in params:
                continue
            val = params[key]
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                try:
                    widget.setValue(
                        float(val) if isinstance(widget, QDoubleSpinBox) else int(val)
                    )
                except (ValueError, TypeError):
                    pass
            elif isinstance(widget, QComboBox):
                idx = widget.findText(str(val))
                if idx >= 0:
                    widget.setCurrentIndex(idx)
                else:
                    try:
                        widget.setCurrentIndex(int(val))
                    except (ValueError, TypeError):
                        pass

        # Tabelas ratio e nratio — suporta ambos os formatos (lista ou dict)
        ratio_vals = params.get("ratio_table", params.get("ratio", []))
        if isinstance(ratio_vals, dict):
            # Formato dict: {"min": 100, "500": 95, ...}
            rpm_labels = [
                "min", "500", "1000", "1500", "2000", "2500", "3000",
                "3500", "4000", "4500", "5000", "5500", "6000", "6500",
                "7000", "7500", "8000", "max"
            ]
            for i, rpm_lbl in enumerate(rpm_labels):
                if i < self.tbl_ratio.rowCount():
                    val = ratio_vals.get(rpm_lbl, 100)
                    item = self.tbl_ratio.item(i, 1)
                    if item:
                        item.setText(str(val))
        else:
            # Formato lista: [100, 95, ...]
            for i, v in enumerate(ratio_vals):
                if i < self.tbl_ratio.rowCount():
                    item = self.tbl_ratio.item(i, 1)
                    if item:
                        item.setText(str(v))

        nratio_vals = params.get("nratio_table", params.get("nratio", []))
        if isinstance(nratio_vals, dict):
            # Formato dict: {"n0": 10, "n1": 8, ...}
            for i in range(self.tbl_nratio.rowCount()):
                val = nratio_vals.get(f"n{i}", 0)
                item = self.tbl_nratio.item(i, 1)
                if item:
                    item.setText(str(val))
        else:
            # Formato lista: [10, 8, ...]
            for i, v in enumerate(nratio_vals):
                if i < self.tbl_nratio.rowCount():
                    item = self.tbl_nratio.item(i, 1)
                    if item:
                        item.setText(str(v))

    def gravar_parametros_completos(self):
        """Lê todos os campos da aba de parâmetros e envia para a controladora."""
        cfg = {}
        for key, widget in self.params_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                cfg[key] = widget.value()
            elif isinstance(widget, QComboBox):
                cfg[key] = widget.currentIndex()

        # Tabelas
        ratio = []
        for i in range(self.tbl_ratio.rowCount()):
            item = self.tbl_ratio.item(i, 1)
            try:
                ratio.append(int(item.text()) if item else 100)
            except ValueError:
                ratio.append(100)
        cfg["ratio"] = ratio

        nratio = []
        for i in range(self.tbl_nratio.rowCount()):
            item = self.tbl_nratio.item(i, 1)
            try:
                nratio.append(int(item.text()) if item else 0)
            except ValueError:
                nratio.append(0)
        cfg["nratio"] = nratio

        if hasattr(
            self.backend, "enviar_configuracoes"
        ) and self.backend.enviar_configuracoes(cfg):
            QMessageBox.information(
                self, "Sucesso", "Parâmetros completos enviados para a controladora."
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue primeiro o dispositivo!")

    def _populate_params_from_backend(self):
        """Busca os parâmetros do backend e popula a aba."""
        if hasattr(self.backend, "get_params"):
            params = self.backend.get_params()
            if params:
                self.populate_params_tab(params)

    # =========================================================================
    # ERROS
    # =========================================================================

    def _limpar_historico_erros(self):
        self.lst_erros.clear()
        if hasattr(self.backend, "error_history"):
            self.backend.error_history.clear()

    def _update_error_log(self):
        """Sincroniza a QListWidget com o histórico de erros do backend."""
        if not hasattr(self.backend, "error_history"):
            return
        history = self.backend.error_history
        current_count = self.lst_erros.count()
        if len(history) == current_count:
            return
        self.lst_erros.clear()
        for entry in history:
            if isinstance(entry, dict):
                ts = entry.get("time", "??:??:??")
                code = entry.get("code", "???")
                desc = entry.get("desc", "Erro desconhecido")
                text = f"[{ts}]  {code}  —  {desc}"
            else:
                text = str(entry)
            item = QListWidgetItem(text)
            item.setForeground(Qt.red)
            self.lst_erros.addItem(item)
        self.lst_erros.scrollToBottom()

    # =========================================================================
    # COLETA DE DADOS
    # =========================================================================

    def _iniciar_coleta_dados(self):
        if hasattr(self.backend, "iniciar_coleta_dados"):
            self.backend.iniciar_coleta_dados()
            QMessageBox.information(
                self,
                "Coleta Iniciada",
                "Gravação de 2048 amostras iniciada!\n\n"
                "Acelere o motor ao máximo por ~20 segundos.",
            )
        else:
            QMessageBox.warning(
                self,
                "Não disponível",
                "Função de coleta não suportada nesta versão do backend.",
            )

    # =========================================================================
    # INDICADORES DE STATUS
    # =========================================================================

    def _update_status_indicators(self, t):
        self.lbl_forward.setStyleSheet(
            "color: #00FF00; font-size: 10px; font-weight: bold;"
            if t.get("forward")
            else "color: #333; font-size: 10px;"
        )
        self.lbl_reverse.setStyleSheet(
            "color: #FFA500; font-size: 10px; font-weight: bold;"
            if t.get("reverse")
            else "color: #333; font-size: 10px;"
        )
        self.lbl_brake.setStyleSheet(
            "color: #FF4B4B; font-size: 10px; font-weight: bold;"
            if t.get("brake")
            else "color: #333; font-size: 10px;"
        )
        self.lbl_motion.setStyleSheet(
            "color: #00AAFF; font-size: 10px; font-weight: bold;"
            if t.get("motion")
            else "color: #333; font-size: 10px;"
        )

    # =========================================================================
    # WATCHDOG / RECONEXÃO AUTOMÁTICA
    # =========================================================================

    def _on_watchdog_disconnect(self):
        """Chamado pelo watchdog do backend quando o cabo é desconectado."""
        QTimer.singleShot(0, self._handle_watchdog_disconnect)

    def _handle_watchdog_disconnect(self):
        if not self.backend.conectado:
            return
        self.timer.stop()
        self.backend.desconectar()
        self.lbl_status.setText("CABO DESCONECTADO")
        self.lbl_status.setStyleSheet(
            "background-color: rgba(255,165,0,0.15); color: #FFA500; padding: 10px; font-weight: bold;"
        )
        self.lbl_erro.setText("⚠️ CABO DESCONECTADO")
        self.lbl_erro.setStyleSheet("color: #FFA500;")
        self.btn_ligar.setText("Ligar / Desligar")
        self.hall_widget.update_state(0, 0, 0)
        QMessageBox.warning(
            self,
            "Conexão Perdida",
            "O cabo USB foi desconectado ou a controladora parou de responder.\n"
            "Verifique a conexão e clique em 'Ligar' novamente.",
        )

    # =========================================================================
    # EXPORTAÇÃO CSV
    # =========================================================================

    def exportar_csv(self):
        if not self.hist_rpm_full:
            QMessageBox.warning(self, "Sem Dados", "Não há dados para exportar.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar CSV",
            f"Dados_Leviata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV (*.csv)",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "Amostra",
                    "RPM",
                    "Corrente_A",
                    "Tensao_V",
                    "Potencia_W",
                    "Torque_Nm",
                    "Temp_Motor_C",
                    "Temp_Ctrl_C",
                    "Throttle_V",
                    "Erro",
                    "SOC_%",
                ]
            )
            # Compatibilizar comprimentos
            max_len = len(self.hist_rpm_full)
            for i in range(max_len):
                writer.writerow(
                    [
                        i,
                        self.hist_rpm_full[i] if i < len(self.hist_rpm_full) else "",
                        self.hist_curr_full[i] if i < len(self.hist_curr_full) else "",
                        self.hist_volt_full[i] if i < len(self.hist_volt_full) else "",
                        (self.hist_volt_full[i] * self.hist_curr_full[i]) if (i < len(self.hist_volt_full) and i < len(self.hist_curr_full)) else "",
                        self.hist_torque_full[i] if i < len(getattr(self, 'hist_torque_full', [])) else "",
                        self.hist_temp_motor_full[i] if i < len(self.hist_temp_motor_full) else "",
                        self.hist_temp_ctrl_full[i] if i < len(self.hist_temp_ctrl_full) else "",
                        self.hist_throttle_full[i] if i < len(getattr(self, 'hist_throttle_full', [])) else "",
                        self.hist_error_full[i] if i < len(getattr(self, 'hist_error_full', [])) else "",
                        self.hist_soc_full[i] if i < len(getattr(self, 'hist_soc_full', [])) else "",
                    ]
                )

        QMessageBox.information(self, "CSV Exportado", f"Arquivo salvo em:\n{path}")

    # =========================================================================
    # PERFIS JSON
    # =========================================================================

    def salvar_perfil(self):
        """Lê todos os campos de params_widgets e salva como JSON."""
        cfg = {}
        for key, widget in self.params_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                cfg[key] = widget.value()
            elif isinstance(widget, QComboBox):
                cfg[key] = widget.currentIndex()

        ratio = []
        for i in range(self.tbl_ratio.rowCount()):
            item = self.tbl_ratio.item(i, 1)
            try:
                ratio.append(int(item.text()) if item else 100)
            except ValueError:
                ratio.append(100)
        cfg["ratio"] = ratio

        nratio = []
        for i in range(self.tbl_nratio.rowCount()):
            item = self.tbl_nratio.item(i, 1)
            try:
                nratio.append(int(item.text()) if item else 0)
            except ValueError:
                nratio.append(0)
        cfg["nratio"] = nratio

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Perfil de Configuração",
            f"Perfil_Leviata_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            "JSON (*.json)",
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Perfil Salvo", f"Perfil salvo em:\n{path}")
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Não foi possível salvar o perfil:\n{e}"
            )

    def carregar_perfil(self):
        """Abre um arquivo JSON e popula a aba de parâmetros."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Carregar Perfil de Configuração",
            "",
            "JSON (*.json);;Todos os Arquivos (*)",
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.populate_params_tab(cfg)
            QMessageBox.information(
                self, "Perfil Carregado", "Perfil aplicado com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Não foi possível carregar o perfil:\n{e}"
            )

    # =========================================================================
    # PORTAS / CONEXÃO
    # =========================================================================

    def atualizar_lista_portas(self):
        self.cb_portas.clear()
        try:
            portas_disponiveis = [
                port.device for port in serial.tools.list_ports.comports()
            ]
            if not portas_disponiveis:
                self.cb_portas.addItems(["Nenhuma porta detetada"])
                self.cb_portas.setEnabled(False)
            else:
                self.cb_portas.addItems(portas_disponiveis)
                self.cb_portas.setEnabled(True)
        except Exception:
            self.cb_portas.addItems(["Erro de permissão"])
            self.cb_portas.setEnabled(False)

    def carregar_ficheiro_heb(self):
        options = QFileDialog.Options()
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Backup Fardriver",
            "",
            "Ficheiros Fardriver (*.heb);;Todos os Ficheiros (*)",
            options=options,
        )
        if filepath:
            try:
                dados_extraidos = HebParser.parse_file(filepath)
                self.sl_polos.setValue(dados_extraidos["pole_pairs"])
                self.sl_linha.setValue(int(dados_extraidos["line_curr"]))
                self.sl_fase.setValue(int(dados_extraidos["phase_curr"]))
                self.cb_throttle.setCurrentIndex(dados_extraidos["throttle_mode"])
                self.cb_weaka.setCurrentIndex(dados_extraidos["weaka_level"])
                QMessageBox.information(
                    self,
                    "Leitura Concluída",
                    "SUCESSO! Ficheiro lido.\nVerifique os campos à esquerda.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro Fatal",
                    f"Ocorreu um erro ao processar o ficheiro:\n{str(e)}",
                )

    def toggle_lock(self):
        is_locked = "Desbloquear" in self.btn_lock.text()
        self.btn_lock.setText("🔓 Bloquear" if is_locked else "🔒 Desbloquear")
        self.btn_lock.setStyleSheet(
            "color: #FF4B4B; border: 1px solid #FF4B4B;" if is_locked else ""
        )
        for w in self.widgets_config:
            w.setEnabled(is_locked)

    def toggle_conexao(self):
        if not self.backend.conectado:
            porta_selecionada = self.cb_portas.currentText()
            if "Nenhuma" in porta_selecionada or "Erro" in porta_selecionada:
                QMessageBox.warning(
                    self, "Aviso", "Ligue o cabo USB da controladora primeiro!"
                )
                return
            sucesso, mensagem_erro = self.backend.conectar(porta_selecionada)
            if sucesso:
                self.lbl_status.setText("ONLINE")
                self.lbl_status.setStyleSheet(
                    "background-color: rgba(0, 255, 0, 0.1); color: #00FF00; padding: 10px; font-weight: bold;"
                )
                self.lbl_erro.setText("SISTEMA OK")
                self.lbl_erro.setStyleSheet("color: #00FF00;")
                self.btn_ligar.setText("Desligar")
                self.timer.start(100)
                # Aguarda 1.5s para os parâmetros chegarem e popula a aba
                QTimer.singleShot(1500, self._populate_params_from_backend)
            else:
                QMessageBox.critical(
                    self,
                    "Falha na Comunicação USB",
                    f"Não foi possível abrir a porta.\n\n{mensagem_erro}",
                )
        else:
            self.backend.desconectar()
            self.lbl_status.setText("DESLIGADO")
            self.lbl_status.setStyleSheet(
                "background-color: #262730; color: #FF4B4B; padding: 10px;"
            )
            self.lbl_erro.setText("AGUARDAR LIGAÇÃO...")
            self.lbl_erro.setStyleSheet("color: #A0A0A0;")
            self.btn_ligar.setText("Ligar / Desligar")
            self.timer.stop()
            self.hall_widget.update_state(0, 0, 0)
            self.hist_rpm_full.clear()
            self.hist_curr_full.clear()
            self.hist_volt_full.clear()
            self.hist_temp_motor_full.clear()
            self.hist_temp_ctrl_full.clear()
            self._tick = 0

    # =========================================================================
    # PARÂMETROS (sidebar simples)
    # =========================================================================

    def gravar_parametros(self):
        cfg = {
            "linha_a": self.sl_linha.value(),
            "fase_a": self.sl_fase.value(),
            "regen_a": self.sl_regen.value(),
            "polos": self.sl_polos.value(),
            "weaka": self.cb_weaka.currentIndex(),
            "throttle": self.cb_throttle.currentIndex(),
        }
        if self.backend.enviar_configuracoes(cfg):
            QMessageBox.information(
                self, "Sucesso", "Parâmetros enviados para a controladora."
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue primeiro o dispositivo!")

    def iniciar_autolearn(self):
        if self.backend.iniciar_autolearn():
            QMessageBox.information(
                self,
                "Auto-Learn Iniciado",
                "Comando enviado!\n\n"
                "Aguarde 2 bipes curtos + 1 longo da controladora.\n"
                "Suspenda a roda e acelere ao máximo até o motor parar sozinho.",
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def cancelar_autolearn(self):
        if self.backend.cancelar_autolearn():
            QMessageBox.information(
                self,
                "Auto-Learn Cancelado",
                "Comando de cancelamento enviado à controladora.",
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def restaurar_fabrica(self):
        resposta = QMessageBox.question(
            self,
            "ALERTA CRÍTICO - RESTAURAR DE FÁBRICA",
            "⚠️ ATENÇÃO: Deseja prosseguir com o Factory Reset?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resposta == QMessageBox.Yes:
            if self.backend.restaurar_fabrica():
                QMessageBox.information(
                    self, "Restauro Concluído", "Controladora restaurada."
                )
            else:
                QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    # =========================================================================
    # LOOP DE TELEMETRIA
    # =========================================================================

    def update_telemetry_loop(self):
        t = self.backend.ler_dados()

        # Cards principais
        self.card_rpm.update_data(t["rpm"], t["rpm"] - self.prev_telemetry["rpm"])
        self.card_volt.update_data(t["volt"], t["volt"] - self.prev_telemetry["volt"])
        self.card_curr.update_data(
            t["curr"], t["curr"] - self.prev_telemetry["curr"], True
        )
        self.card_power.update_data(
            t["power"], t["power"] - self.prev_telemetry["power"], True
        )

        # Card SOC
        soc_val = t.get("batt_soc", 0)
        soc_delta = soc_val - self.prev_telemetry.get("batt_soc", 0)
        self.card_soc.update_data(soc_val, soc_delta)
        
        # Alerta de bateria baixa (< 20%)
        if soc_val < 20:
            self.card_soc.setStyleSheet(
                "background-color: rgba(255,75,75,0.15); border: 1px solid #FF4B4B; border-radius: 4px;"
            )
        elif soc_val < 50:
            self.card_soc.setStyleSheet(
                "background-color: rgba(255,165,0,0.15); border: 1px solid #FFA500; border-radius: 4px;"
            )
        else:
            self.card_soc.setStyleSheet("")

        self.card_torque.update_data(
            t["torque"], t["torque"] - self.prev_telemetry["torque"], True
        )
        self.card_temp.update_data(t["temp_motor"], 0, True)
        self.card_temp_ctrl.update_data(t["temp_mosfet"], 0, True)
        self.card_throttle.update_data(t["throttle"], 0)

        # Alertas visuais de temperatura
        temp_motor = t.get("temp_motor", 0)
        temp_ctrl = t.get("temp_mosfet", 0)
        
        # Motor: amarelo >80°C, vermelho >95°C
        if temp_motor > 95:
            self.card_temp.setStyleSheet(
                "background-color: rgba(255,75,75,0.25); border: 2px solid #FF4B4B; border-radius: 4px;"
            )
        elif temp_motor > 80:
            self.card_temp.setStyleSheet(
                "background-color: rgba(255,165,0,0.15); border: 1px solid #FFA500; border-radius: 4px;"
            )
        else:
            self.card_temp.setStyleSheet("")
        
        # Controladora: amarelo >70°C, vermelho >85°C
        if temp_ctrl > 85:
            self.card_temp_ctrl.setStyleSheet(
                "background-color: rgba(255,75,75,0.25); border: 2px solid #FF4B4B; border-radius: 4px;"
            )
        elif temp_ctrl > 70:
            self.card_temp_ctrl.setStyleSheet(
                "background-color: rgba(255,165,0,0.15); border: 1px solid #FFA500; border-radius: 4px;"
            )
        else:
            self.card_temp_ctrl.setStyleSheet("")

        # Hall sensors
        self.hall_widget.update_state(t["hall_a"], t["hall_b"], t["hall_c"])

        # Indicadores de status
        self._update_status_indicators(t)
        
        # Atualiza barra de status inferior
        if self.backend.conectado:
            self.lbl_status_connection.setText("Status: ◉ Online")
            self.lbl_status_connection.setStyleSheet("color: #00FF00; font-size: 10px; font-weight: bold;")
        else:
            self.lbl_status_connection.setText("Status: ◯ Offline")
            self.lbl_status_connection.setStyleSheet("color: #FF4B4B; font-size: 10px;")
        
        # Contagem de erros
        error_count = len(self.backend.get_error_history()) if hasattr(self.backend, 'get_error_history') else 0
        self.lbl_status_errors.setText(f"Erros: {error_count}")
        
        # Taxa de dados (aproximado: 10 Hz com atualização a cada 100ms)
        self.lbl_status_datarate.setText("Taxa: ~10 Hz")
        
        # Contador de pacotes (baseado em _tick)
        self.lbl_status_packets.setText(f"Pacotes: {self._tick}")

        self.prev_telemetry = t.copy()

        # Histórico completo (para relatório)
        self.hist_rpm_full.append(t["rpm"])
        self.hist_curr_full.append(t["curr"])
        self.hist_volt_full.append(t["volt"])
        self.hist_temp_motor_full.append(t["temp_motor"])
        self.hist_temp_ctrl_full.append(t["temp_mosfet"])
        self.hist_torque_full.append(t.get("torque", 0))
        self.hist_throttle_full.append(t.get("throttle", 0.0))
        self.hist_error_full.append(t.get("error", 0))
        self.hist_soc_full.append(t.get("batt_soc", 0))

        # Atualiza gráficos (janela deslizante)
        self._tick += 1
        n = min(self._tick, self.max_pts_tela)
        eixo_x_tela = list(range(self._tick - n, self._tick))

        self.l_rpm.setData(eixo_x_tela, self.hist_rpm_full[-self.max_pts_tela :])
        self.l_curr.setData(eixo_x_tela, self.hist_curr_full[-self.max_pts_tela :])
        self.l_volt.setData(eixo_x_tela, self.hist_volt_full[-self.max_pts_tela :])

        # Atualiza log de erros a cada 30 ticks
        if self._tick % 30 == 0:
            self._update_error_log()

    # =========================================================================
    # GERADOR DE RELATÓRIO HTML OFFLINE
    # =========================================================================

    def gerar_relatorio_html(self):
        if not self.hist_rpm_full:
            QMessageBox.warning(
                self,
                "Sem Dados",
                "Não há dados para exportar! Ligue a controladora e aguarde a leitura do gráfico.",
            )
            return

        t = self.backend.ler_dados()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        caminho_salvar, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório de Teste",
            f"Relatorio_Leviata_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            "Arquivos Web (*.html)",
            options=options,
        )

        if not caminho_salvar:
            return

        STEP = max(1, len(self.hist_rpm_full) // 3000)
        rpm_dec = self.hist_rpm_full[::STEP]
        curr_dec = self.hist_curr_full[::STEP]
        volt_dec = self.hist_volt_full[::STEP]
        temp_motor_dec = self.hist_temp_motor_full[::STEP]
        temp_ctrl_dec = self.hist_temp_ctrl_full[::STEP]
        eixo_dec = list(range(len(rpm_dec)))

        pasta_escolhida = os.path.dirname(caminho_salvar)

        from report_generator import ReportGenerator

        caminho_gerado = ReportGenerator.generate_html_report(
            t,
            rpm_dec,
            curr_dec,
            volt_dec,
            eixo_dec,
            pasta_escolhida,
            temp_motor_dec,
            temp_ctrl_dec,
        )

        if (
            caminho_gerado
            and os.path.isfile(caminho_gerado)
            and caminho_gerado != caminho_salvar
        ):
            os.replace(caminho_gerado, caminho_salvar)
