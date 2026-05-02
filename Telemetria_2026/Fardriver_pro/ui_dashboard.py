import csv
import json
import logging
import os
import sys
import webbrowser
from datetime import datetime

import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDesktopWidget,
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
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """Resolve path for both dev and PyInstaller .exe environments."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


from fardriver_serial import FardriverSerial
from heb_parser import HebParser
from report_generator import ReportGenerator

# ==============================================================================
# Stylesheet
# ==============================================================================
STYLESHEET = """
QMainWindow { background-color: #0E1117; }
QWidget { background-color: #0E1117; color: #FAFAFA; font-family: "Segoe UI", Arial, sans-serif; }
QLabel { color: #FAFAFA; }
QFrame#Sidebar { background-color: #262730; border-right: 1px solid #333333; }

QPushButton {
    background-color: #262730; color: white;
    border: 1px solid #4B4C52; padding: 8px;
    border-radius: 4px; font-weight: bold;
}
QPushButton:hover { border: 1px solid #FF4B4B; color: #FF4B4B; }
QPushButton:disabled { background-color: #1a1b20; color: #555555; border: 1px solid #333333; }
QPushButton#BtnLigar:hover { border: 1px solid #00FF00; color: #00FF00; }
QPushButton#BtnHeb { background-color: #005580; border: 1px solid #00AAFF; }
QPushButton#BtnHeb:hover { background-color: #00AAFF; color: black; }
QPushButton#BtnFactoryReset { background-color: #8B0000; color: white; border: 1px solid #FF0000; }
QPushButton#BtnFactoryReset:hover { background-color: #FF0000; }
QPushButton#BtnRelatorio { background-color: #198754; color: white; border: 1px solid #146c43; }
QPushButton#BtnRelatorio:hover { background-color: #157347; }
QPushButton#BtnCsv { background-color: #0d6efd; color: white; border: 1px solid #0b5ed7; }
QPushButton#BtnCsv:hover { background-color: #0b5ed7; }

QComboBox {
    background-color: #262730; color: white;
    border: 1px solid #4B4C52; padding: 5px; border-radius: 4px;
}
QComboBox:disabled { background-color: #1a1b20; color: #555555; }
QComboBox QAbstractItemView { background-color: #262730; color: white; selection-background-color: #FF4B4B; }

QSlider::groove:horizontal { border: 1px solid #4B4C52; height: 4px; background: #4B4C52; border-radius: 2px; }
QSlider::handle:horizontal { background: #FF4B4B; border: 1px solid #FF4B4B; width: 14px; height: 14px; margin: -6px 0; border-radius: 7px; }
QSlider::sub-page:horizontal { background: #FF4B4B; border-radius: 2px; }
QSlider::groove:horizontal:disabled { background: #333333; border: 1px solid #333333; }
QSlider::handle:horizontal:disabled { background: #555555; border: 1px solid #555555; }
QSlider::sub-page:horizontal:disabled { background: #555555; }

QScrollArea { border: none; background-color: transparent; }
QScrollBar:vertical { border: none; background: #262730; width: 8px; }
QScrollBar::handle:vertical { background: #4B4C52; border-radius: 4px; }
QScrollBar:horizontal { border: none; background: #262730; height: 8px; }
QScrollBar::handle:horizontal { background: #4B4C52; border-radius: 4px; }

QMessageBox { background-color: #262730; }
QMessageBox QLabel { color: #FAFAFA; background-color: transparent; }
QMessageBox QPushButton { background-color: #0E1117; color: white; border: 1px solid #4B4C52; min-width: 80px; padding: 5px; }
QMessageBox QPushButton:hover { border: 1px solid #00AAFF; color: #00AAFF; }

QTabWidget::pane { border: 1px solid #333; background-color: #0E1117; }
QTabBar::tab { background: #262730; color: #A0A0A0; padding: 8px 16px; border: 1px solid #333; margin-right: 2px; }
QTabBar::tab:selected { background: #0E1117; color: #FAFAFA; border-bottom: 2px solid #FF4B4B; }
QTabBar::tab:hover { color: #FAFAFA; }

QGroupBox {
    color: #A0A0A0; border: 1px solid #333; margin-top: 12px;
    padding-top: 10px; border-radius: 4px;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #FF4B4B; font-weight: bold; }

QSpinBox, QDoubleSpinBox {
    background-color: #262730; color: white;
    border: 1px solid #4B4C52; padding: 4px; border-radius: 4px;
}
QSpinBox:disabled, QDoubleSpinBox:disabled { background-color: #1a1b20; color: #555555; }

QTableWidget { background-color: #0E1117; color: white; gridline-color: #333333; border: 1px solid #333; }
QTableWidget::item { padding: 4px; }
QTableWidget::item:selected { background-color: #FF4B4B; color: white; }
QHeaderView::section { background-color: #262730; color: #A0A0A0; padding: 6px; border: 1px solid #333; font-weight: bold; }

QListWidget { background-color: #0E1117; color: white; border: 1px solid #333; border-radius: 4px; }
QListWidget::item { padding: 4px 8px; border-bottom: 1px solid #1a1b20; }
QListWidget::item:selected { background-color: #262730; }
"""

# PID presets (StartKI, MidKI, MaxKI, StartKP, MidKP, MaxKP)
PID_PRESETS = {
    "Motor Pequena Potência": (8, 8, 12, 80, 80, 120),
    "Potência Média": (6, 6, 9, 60, 60, 90),
    "Alta Potência": (4, 4, 6, 40, 40, 60),
    "Ultra Alta Potência": (2, 2, 3, 20, 20, 30),
    "Personalizado": None,
}

RPM_LABELS = [
    "min",
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
    "max",
]


# ==============================================================================
# Reusable widgets
# ==============================================================================


class MetricCard(QFrame):
    def __init__(self, title, unit=""):
        super().__init__()
        self.unit = unit
        self._base_style = ""
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
        arrow = "↑" if is_pos else "↓"
        self.lbl_delta.setText(f"{arrow} {abs(delta_val):.1f} {self.unit}")
        if (is_pos and not reverse_color) or (not is_pos and reverse_color):
            self.lbl_delta.setStyleSheet(
                "color: #00FF00; background-color: rgba(0,255,0,0.1); padding: 2px; border-radius: 3px;"
            )
        else:
            self.lbl_delta.setStyleSheet(
                "color: #FF4B4B; background-color: rgba(255,75,75,0.1); padding: 2px; border-radius: 3px;"
            )

    def set_alert(self, active: bool):
        if active:
            self.setStyleSheet(
                "background-color: rgba(255,75,75,0.15); border: 1px solid #FF4B4B; border-radius: 4px;"
            )
        else:
            self.setStyleSheet(self._base_style)


class HallSensorsWidget(QFrame):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
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


class StatusIndicator(QLabel):
    def __init__(self, text, active_color="#00FF00"):
        super().__init__(text)
        self._active_color = active_color
        self._inactive = (
            "color: #333; font-size: 10px; font-weight: bold; padding: 2px 6px;"
        )
        self._active = f"color: {active_color}; font-size: 10px; font-weight: bold; padding: 2px 6px; background-color: rgba(0,0,0,0.3); border-radius: 3px;"
        self.setStyleSheet(self._inactive)

    def set_active(self, active: bool):
        self.setStyleSheet(self._active if active else self._inactive)


# ==============================================================================
# Main Application
# ==============================================================================


class FardriverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro — Bancada de Testes · Leviatã UEA")

        # --- Tamanho mínimo garantido, inicial adaptativo ---
        self.setMinimumSize(1024, 600)

        screen_geom = QDesktopWidget().availableGeometry()
        target_w = min(1440, int(screen_geom.width() * 0.9))
        target_h = min(860, int(screen_geom.height() * 0.9))
        self.resize(target_w, target_h)
        self.setStyleSheet(STYLESHEET)

        self.backend = FardriverSerial()
        self.backend.on_disconnect_callback = self._on_watchdog_disconnect
        self.prev_telemetry = self.backend.ler_dados()

        # History buffers
        self.max_pts_tela = 100
        self.hist_rpm_full = []
        self.hist_curr_full = []
        self.hist_volt_full = []
        self.hist_temp_motor_full = []
        self.hist_temp_ctrl_full = []
        self._tick = 0

        self._setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry_loop)

    # ──────────────────────────────────────────────────────────────────
    # UI construction
    # ──────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Splitter horizontal (sidebar | conteúdo) ---
        self.main_splitter = QSplitter(Qt.Horizontal)

        sidebar = self._build_sidebar()
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self._build_dashboard_tab(), "📊 Dashboard")
        self.tab_widget.addTab(self._build_params_tab(), "⚙️ Parâmetros")
        self.tab_widget.addTab(self._build_data_collection_tab(), "📈 Coleta de Dados")
        self.tab_widget.addTab(self._build_error_log_tab(), "📋 Erros")

        self.main_splitter.addWidget(sidebar)
        self.main_splitter.addWidget(self.tab_widget)

        # Configuração do splitter
        self.main_splitter.setStretchFactor(0, 0)  # sidebar não estica
        self.main_splitter.setStretchFactor(1, 1)  # área do tab expande
        self.main_splitter.setSizes(
            [300, 1140]
        )  # proporção inicial (igual ao original)
        self.main_splitter.setHandleWidth(1)  # divisor fino

        root_layout.addWidget(self.main_splitter)

    # ── Sidebar ───────────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(250)  # impede que fique demasiado estreita
        sidebar.setMaximumWidth(450)  # opcional: evita que roube demasiado espaço
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QFrame()
        hdr_layout = QVBoxLayout(hdr)
        hdr_layout.setContentsMargins(16, 16, 16, 10)
        hdr_layout.setSpacing(8)

        # Logo + title
        logo_row = QHBoxLayout()
        lbl_logo = QLabel()
        logo_path = resource_path("logo.png")
        pix = QPixmap(logo_path)
        if not pix.isNull():
            lbl_logo.setPixmap(
                pix.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            logo_row.addWidget(lbl_logo)
        logo_row.addWidget(
            QLabel("Fardriver Pro", font=QFont("Segoe UI", 15, QFont.Bold))
        )
        logo_row.addStretch()
        hdr_layout.addLayout(logo_row)
        hdr_layout.addWidget(
            QLabel(
                "Bancada de Testes — Leviatã UEA",
                styleSheet="color:#A0A0A0; font-size:10px;",
            )
        )

        # Port selector
        port_row = QHBoxLayout()
        self.cb_portas = QComboBox()
        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedWidth(32)
        self.btn_refresh.setToolTip("Atualizar lista de portas")
        self.btn_refresh.clicked.connect(self.atualizar_lista_portas)
        port_row.addWidget(self.cb_portas)
        port_row.addWidget(self.btn_refresh)
        hdr_layout.addLayout(port_row)
        self.atualizar_lista_portas()

        self.btn_ligar = QPushButton("Ligar / Desligar")
        self.btn_ligar.setObjectName("BtnLigar")
        self.btn_ligar.clicked.connect(self.toggle_conexao)
        hdr_layout.addWidget(self.btn_ligar)

        self.lbl_status = QLabel("Desligado")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet(
            "background-color:#262730; color:#FF4B4B; padding:8px; border-radius:4px;"
        )
        hdr_layout.addWidget(self.lbl_status)

        layout.addWidget(hdr)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color:#4B4C52; margin:0 12px;")
        layout.addWidget(div)

        # Scrollable config area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")
        content = QFrame()
        content.setStyleSheet("background:transparent;")
        side_layout = QVBoxLayout(content)
        side_layout.setContentsMargins(16, 10, 16, 16)
        side_layout.setSpacing(10)

        # Action buttons
        self.btn_load_heb = QPushButton("📂 Carregar Backup (.HEB)")
        self.btn_load_heb.setObjectName("BtnHeb")
        self.btn_load_heb.clicked.connect(self.carregar_ficheiro_heb)
        side_layout.addWidget(self.btn_load_heb)

        self.btn_relatorio = QPushButton("📄 Gerar Relatório Web")
        self.btn_relatorio.setObjectName("BtnRelatorio")
        self.btn_relatorio.clicked.connect(self.gerar_relatorio_html)
        side_layout.addWidget(self.btn_relatorio)

        self.btn_csv = QPushButton("📊 Exportar CSV")
        self.btn_csv.setObjectName("BtnCsv")
        self.btn_csv.clicked.connect(self.exportar_csv)
        side_layout.addWidget(self.btn_csv)

        # Profile buttons
        profile_row = QHBoxLayout()
        self.btn_salvar_perfil = QPushButton("💾 Salvar Perfil")
        self.btn_carregar_perfil = QPushButton("📂 Carregar Perfil")
        self.btn_salvar_perfil.clicked.connect(self.salvar_perfil)
        self.btn_carregar_perfil.clicked.connect(self.carregar_perfil)
        profile_row.addWidget(self.btn_salvar_perfil)
        profile_row.addWidget(self.btn_carregar_perfil)
        side_layout.addLayout(profile_row)

        side_layout.addWidget(self._make_divider())

        # Sliders
        side_layout.addWidget(
            QLabel("Configurações Rápidas", font=QFont("Segoe UI", 10, QFont.Bold))
        )

        lock_row = QHBoxLayout()
        lock_row.addWidget(QLabel("Edição de parâmetros:"))
        self.btn_lock = QPushButton("🔒 Desbloquear")
        self.btn_lock.setFixedWidth(110)
        self.btn_lock.clicked.connect(self.toggle_lock)
        lock_row.addWidget(self.btn_lock)
        side_layout.addLayout(lock_row)

        self.widgets_config = []

        def add_slider(label, min_v, max_v, default):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            val_lbl = QLabel(str(default))
            val_lbl.setStyleSheet("color:#FF4B4B; font-weight:bold;")
            row.addWidget(val_lbl, alignment=Qt.AlignRight)
            side_layout.addLayout(row)
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

        side_layout.addWidget(QLabel("Resposta do Acelerador:"))
        self.cb_throttle = QComboBox()
        self.cb_throttle.addItems(
            ["Linear (Padrão)", "Sport (Agressivo)", "ECO (Econômico)", "Inválido (3)"]
        )
        self.cb_throttle.setEnabled(False)
        side_layout.addWidget(self.cb_throttle)

        side_layout.addWidget(QLabel("Campo Fraco (Weak Field):"))
        self.cb_weaka = QComboBox()
        self.cb_weaka.addItems(
            ["Nível 0 (Desligado)", "Nível 1", "Nível 2", "Nível 3 (Máximo)"]
        )
        self.cb_weaka.setEnabled(False)
        side_layout.addWidget(self.cb_weaka)

        side_layout.addWidget(QLabel("Sensor Temp. Motor:"))
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

        # Auto-learn row
        al_row = QHBoxLayout()
        self.btn_autolearn = QPushButton("⚙️ Auto-Aprendizado")
        self.btn_autolearn.setEnabled(False)
        self.btn_autolearn.clicked.connect(self.iniciar_autolearn)
        self.btn_cancel_autolearn = QPushButton("✖ Cancelar Learn")
        self.btn_cancel_autolearn.setEnabled(False)
        self.btn_cancel_autolearn.setStyleSheet(
            "QPushButton{color:#FFA500;border:1px solid #FFA500;}"
            "QPushButton:hover{background-color:#FFA500;color:black;}"
            "QPushButton:disabled{color:#555;border:1px solid #333;}"
        )
        self.btn_cancel_autolearn.clicked.connect(self.cancelar_autolearn)
        al_row.addWidget(self.btn_autolearn)
        al_row.addWidget(self.btn_cancel_autolearn)
        side_layout.addLayout(al_row)

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
        scroll.setWidget(content)
        layout.addWidget(scroll)
        return sidebar

    # ── Dashboard tab ─────────────────────────────────────────────────

    def _build_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header row
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.addWidget(
            QLabel(
                "⚡ Painel de Telemetria Fardriver",
                font=QFont("Segoe UI", 22, QFont.Bold),
            )
        )
        title_box.addWidget(
            QLabel("Bancada de Testes — Leviatã UEA", styleSheet="color:#A0A0A0;")
        )
        hdr.addLayout(title_box)
        hdr.addStretch()

        # Status indicators
        status_col = QVBoxLayout()
        self.hall_widget = HallSensorsWidget()
        status_col.addWidget(self.hall_widget)

        status_row = QHBoxLayout()
        self.ind_forward = StatusIndicator("▶ MARCHA", "#00FF00")
        self.ind_reverse = StatusIndicator("◀ RÉ", "#FFA500")
        self.ind_brake = StatusIndicator("⬛ FREIO", "#FF4B4B")
        self.ind_motion = StatusIndicator("◉ MOVER", "#00AAFF")
        for ind in (
            self.ind_forward,
            self.ind_reverse,
            self.ind_brake,
            self.ind_motion,
        ):
            status_row.addWidget(ind)
        status_col.addLayout(status_row)
        hdr.addLayout(status_col)

        self.lbl_erro = QLabel("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.lbl_erro.setAlignment(Qt.AlignRight | Qt.AlignTop)
        hdr.addWidget(self.lbl_erro)
        layout.addLayout(hdr)

        # Top metric cards — row 1
        row1 = QHBoxLayout()
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
            row1.addWidget(c)
        layout.addLayout(row1)

        # Row 2
        row2 = QHBoxLayout()
        self.card_torque = MetricCard("Torque", "N·m")
        self.card_temp = MetricCard("Temp. Motor", "°C")
        self.card_temp_ctrl = MetricCard("Temp. Controladora", "°C")
        self.card_throttle = MetricCard("Acelerador", "V")
        self.card_phase_off = MetricCard("Offset de Fase", "°")
        for c in (
            self.card_torque,
            self.card_temp,
            self.card_temp_ctrl,
            self.card_throttle,
            self.card_phase_off,
        ):
            row2.addWidget(c)
        layout.addLayout(row2)

        # Charts
        layout.addWidget(
            QLabel(
                "Análise de Desempenho Real-Time",
                font=QFont("Segoe UI", 14, QFont.Bold),
            )
        )
        pg.setConfigOption("background", "#0E1117")
        pg.setConfigOption("foreground", "#A0A0A0")

        charts = QHBoxLayout()
        self.p_volt = pg.PlotWidget(title="Tensão de Bateria (V)")
        self.p_volt.setYRange(40, 60)
        self.l_volt = self.p_volt.plot(pen=pg.mkPen("#00AAFF", width=2))

        self.p_curr = pg.PlotWidget(title="Corrente Linha (A)")
        self.p_curr.setYRange(-5, 150)
        self.l_curr = self.p_curr.plot(pen=pg.mkPen("#FF4B4B", width=2))

        self.p_rpm = pg.PlotWidget(title="Rotação do Motor (RPM)")
        self.p_rpm.setYRange(0, 6000)
        self.l_rpm = self.p_rpm.plot(pen=pg.mkPen("#00FF00", width=2))

        for p in (self.p_volt, self.p_curr, self.p_rpm):
            p.showGrid(y=True, alpha=0.2)
            p.getAxis("bottom").setStyle(showValues=False)
            charts.addWidget(p)
        layout.addLayout(charts)
        # Largura mínima dos gráficos
        self.p_volt.setMinimumWidth(200)
        self.p_curr.setMinimumWidth(200)
        self.p_rpm.setMinimumWidth(200)

        return tab

    # ── Parameters tab ────────────────────────────────────────────────

    def _build_params_tab(self):
        tab = QWidget()
        outer = QVBoxLayout(tab)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self.params_widgets = {}

        # Info banner
        self.lbl_fw_info = QLabel("Versão do firmware: — | Hardware: —")
        self.lbl_fw_info.setStyleSheet(
            "color:#A0A0A0; font-size:11px; padding:6px; background:#262730; border-radius:4px;"
        )
        layout.addWidget(self.lbl_fw_info)

        # ── Motor group ───────────────────────────────────────────────
        grp_motor = QGroupBox("Motor")
        gm = QVBoxLayout(grp_motor)

        def add_param_row(parent_layout, label, widget, key):
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(220)
            row.addWidget(lbl)
            row.addWidget(widget)
            parent_layout.addLayout(row)
            self.params_widgets[key] = widget

        sp_polos = QSpinBox()
        sp_polos.setRange(1, 40)
        sp_polos.setValue(4)
        add_param_row(gm, "Pares de Polos", sp_polos, "pole_pairs")

        sp_rated_speed = QSpinBox()
        sp_rated_speed.setRange(0, 9000)
        sp_rated_speed.setSuffix(" RPM")
        add_param_row(gm, "Velocidade Nominal (RPM)", sp_rated_speed, "rated_speed")

        sp_rated_volt = QDoubleSpinBox()
        sp_rated_volt.setRange(24.0, 120.0)
        sp_rated_volt.setSingleStep(1.0)
        sp_rated_volt.setSuffix(" V")
        add_param_row(gm, "Tensão Nominal (V)", sp_rated_volt, "rated_voltage")

        sp_rated_power = QSpinBox()
        sp_rated_power.setRange(0, 30000)
        sp_rated_power.setSuffix(" W")
        add_param_row(gm, "Potência Nominal (W)", sp_rated_power, "rated_power")

        sp_max_speed = QSpinBox()
        sp_max_speed.setRange(0, 9000)
        sp_max_speed.setSuffix(" RPM")
        add_param_row(gm, "Velocidade Máxima (RPM)", sp_max_speed, "max_speed")

        sp_phase_off = QDoubleSpinBox()
        sp_phase_off.setRange(-360.0, 360.0)
        sp_phase_off.setSingleStep(0.1)
        sp_phase_off.setSuffix(" °")
        add_param_row(gm, "Offset de Fase (°)", sp_phase_off, "phase_offset")

        cb_direction = QComboBox()
        cb_direction.addItems(["Esquerda (Padrão)", "Direita (Invertido)"])
        add_param_row(gm, "Direção do Motor", cb_direction, "direction")

        layout.addWidget(grp_motor)

        # ── Throttle group ────────────────────────────────────────────
        grp_thr = QGroupBox("Acelerador")
        gt = QVBoxLayout(grp_thr)

        sp_thr_low = QDoubleSpinBox()
        sp_thr_low.setRange(0.0, 3.0)
        sp_thr_low.setSingleStep(0.05)
        sp_thr_low.setSuffix(" V")
        add_param_row(gt, "Limiar Baixo (idle)", sp_thr_low, "throttle_low")

        sp_thr_high = QDoubleSpinBox()
        sp_thr_high.setRange(2.0, 5.0)
        sp_thr_high.setSingleStep(0.05)
        sp_thr_high.setSuffix(" V")
        add_param_row(gt, "Limiar Alto (full)", sp_thr_high, "throttle_high")

        layout.addWidget(grp_thr)

        # ── Protections group ─────────────────────────────────────────
        grp_prot = QGroupBox("Proteções")
        gp = QVBoxLayout(grp_prot)

        sp_lv = QDoubleSpinBox()
        sp_lv.setRange(10.0, 100.0)
        sp_lv.setSingleStep(0.5)
        sp_lv.setSuffix(" V")
        add_param_row(gp, "Proteção Subtensão (V)", sp_lv, "low_vol_protect")

        sp_tmp_m = QSpinBox()
        sp_tmp_m.setRange(60, 150)
        sp_tmp_m.setSuffix(" °C")
        add_param_row(gp, "Proteção Temp. Motor (°C)", sp_tmp_m, "motor_temp_protect")

        sp_tmp_c = QSpinBox()
        sp_tmp_c.setRange(60, 120)
        sp_tmp_c.setSuffix(" °C")
        add_param_row(
            gp, "Proteção Temp. Controladora (°C)", sp_tmp_c, "mos_temp_protect"
        )

        layout.addWidget(grp_prot)

        # ── PID group ─────────────────────────────────────────────────
        grp_pid = QGroupBox("PID de Corrente")
        gpid = QVBoxLayout(grp_pid)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Perfil PID:"))
        self.cb_pid_preset = QComboBox()
        self.cb_pid_preset.addItems(list(PID_PRESETS.keys()))
        self.cb_pid_preset.currentTextChanged.connect(self._apply_pid_preset)
        preset_row.addWidget(self.cb_pid_preset)
        gpid.addLayout(preset_row)

        for key, label, lo, hi in [
            ("start_ki", "StartKI", 0, 30),
            ("mid_ki", "MidKI", 0, 30),
            ("max_ki", "MaxKI", 0, 30),
            ("start_kp", "StartKP", 0, 255),
            ("mid_kp", "MidKP", 0, 255),
            ("max_kp", "MaxKP", 0, 255),
        ]:
            sp = QSpinBox()
            sp.setRange(lo, hi)
            add_param_row(gpid, label, sp, key)

        layout.addWidget(grp_pid)

        # ── Current limit table ───────────────────────────────────────
        grp_ratio = QGroupBox("Tabela de Limite de Corrente por RPM (%)")
        gr = QVBoxLayout(grp_ratio)
        self.tbl_ratio = QTableWidget(18, 2)
        self.tbl_ratio.setHorizontalHeaderLabels(["RPM", "Limite (0–100 %)"])
        self.tbl_ratio.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_ratio.setMaximumHeight(420)
        for i, lbl in enumerate(RPM_LABELS):
            self.tbl_ratio.setItem(i, 0, QTableWidgetItem(lbl))
            self.tbl_ratio.item(i, 0).setFlags(Qt.ItemIsEnabled)
            self.tbl_ratio.setItem(i, 1, QTableWidgetItem("100"))
        gr.addWidget(self.tbl_ratio)
        layout.addWidget(grp_ratio)

        # ── Regen table ───────────────────────────────────────────────
        grp_nratio = QGroupBox("Tabela de Frenagem Regenerativa por RPM (%)")
        gnr = QVBoxLayout(grp_nratio)
        self.tbl_nratio = QTableWidget(18, 2)
        self.tbl_nratio.setHorizontalHeaderLabels(["RPM", "Frenagem (-100–0 %)"])
        self.tbl_nratio.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_nratio.setMaximumHeight(420)
        for i, lbl in enumerate(RPM_LABELS):
            self.tbl_nratio.setItem(i, 0, QTableWidgetItem(lbl))
            self.tbl_nratio.item(i, 0).setFlags(Qt.ItemIsEnabled)
            self.tbl_nratio.setItem(i, 1, QTableWidgetItem("0"))
        gnr.addWidget(self.tbl_nratio)
        layout.addWidget(grp_nratio)

        # Footer buttons
        btn_row = QHBoxLayout()
        btn_ler = QPushButton("🔄 Ler da Controladora")
        btn_ler.clicked.connect(self._populate_params_from_backend)
        btn_gravar_tudo = QPushButton("💾 Gravar Tudo na Controladora")
        btn_gravar_tudo.clicked.connect(self.gravar_parametros_completos)
        btn_row.addWidget(btn_ler)
        btn_row.addWidget(btn_gravar_tudo)
        layout.addLayout(btn_row)
        layout.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

        # Largura mínima das colunas das tabelas de ratio
        self.tbl_ratio.horizontalHeader().setMinimumSectionSize(80)
        self.tbl_nratio.horizontalHeader().setMinimumSectionSize(80)

        return tab

    # ── Data collection tab ───────────────────────────────────────────

    def _build_data_collection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(
            QLabel(
                "Coleta de Dados de Aceleração", font=QFont("Segoe UI", 16, QFont.Bold)
            )
        )
        info = QLabel(
            "Inicia a gravação de 2048 amostras do ciclo de aceleração na flash da controladora.\n"
            "Após clicar em Iniciar, acelere o motor ao máximo por aproximadamente 20 segundos."
        )
        info.setStyleSheet(
            "color:#A0A0A0; padding:8px; background:#262730; border-radius:4px;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        btn_start = QPushButton("▶ Iniciar Coleta (2048 amostras)")
        btn_start.clicked.connect(self._iniciar_coleta)
        btn_row.addWidget(btn_start)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Plot for collected data
        self.p_collect = pg.PlotWidget(title="Dados Coletados — RPM vs. Amostra")
        self.p_collect.showGrid(x=True, y=True, alpha=0.2)
        self.p_collect.setLabel("left", "RPM")
        self.p_collect.setLabel("bottom", "Amostra")
        self.l_collect = self.p_collect.plot(pen=pg.mkPen("#00FF00", width=2))
        layout.addWidget(self.p_collect)

        return tab

    # ── Error log tab ─────────────────────────────────────────────────

    def _build_error_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(
            QLabel(
                "Histórico de Erros da Sessão", font=QFont("Segoe UI", 16, QFont.Bold)
            )
        )

        self.lst_erros = QListWidget()
        self.lst_erros.setFont(QFont("Consolas", 10))
        layout.addWidget(self.lst_erros)

        btn_row = QHBoxLayout()
        btn_clear = QPushButton("🗑 Limpar Histórico")
        btn_clear.clicked.connect(self._limpar_historico_erros)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        return tab

    # ──────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────

    def _make_divider(self):
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background-color:#4B4C52;")
        return div

    def atualizar_lista_portas(self):
        self.cb_portas.clear()
        try:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if ports:
                self.cb_portas.addItems(ports)
                self.cb_portas.setEnabled(True)
            else:
                self.cb_portas.addItems(["Nenhuma porta detectada"])
                self.cb_portas.setEnabled(False)
        except Exception:
            self.cb_portas.addItems(["Erro de permissão"])
            self.cb_portas.setEnabled(False)

    # ──────────────────────────────────────────────────────────────────
    # Connection
    # ──────────────────────────────────────────────────────────────────

    def toggle_conexao(self):
        if not self.backend.conectado:
            porta = self.cb_portas.currentText()
            if "Nenhuma" in porta or "Erro" in porta:
                QMessageBox.warning(self, "Aviso", "Ligue o cabo USB primeiro!")
                return
            ok, msg = self.backend.conectar(porta)
            if ok:
                self.lbl_status.setText("ONLINE")
                self.lbl_status.setStyleSheet(
                    "background-color:rgba(0,255,0,0.1); color:#00FF00; padding:8px; font-weight:bold;"
                )
                self.lbl_erro.setText("SISTEMA OK")
                self.lbl_erro.setStyleSheet("color:#00FF00;")
                self.btn_ligar.setText("Desligar")
                self.timer.start(100)
                # Populate params after flash dump arrives
                QTimer.singleShot(2000, self._populate_params_from_backend)
            else:
                QMessageBox.critical(
                    self,
                    "Falha na Conexão",
                    f"Não foi possível abrir a porta.\n\n{msg}",
                )
        else:
            self.backend.desconectar()
            self._reset_ui_after_disconnect()

    def _reset_ui_after_disconnect(self):
        self.lbl_status.setText("DESLIGADO")
        self.lbl_status.setStyleSheet(
            "background-color:#262730; color:#FF4B4B; padding:8px;"
        )
        self.lbl_erro.setText("AGUARDAR LIGAÇÃO...")
        self.lbl_erro.setStyleSheet("color:#A0A0A0;")
        self.btn_ligar.setText("Ligar / Desligar")
        self.timer.stop()
        self.hall_widget.update_state(0, 0, 0)
        for ind in (
            self.ind_forward,
            self.ind_reverse,
            self.ind_brake,
            self.ind_motion,
        ):
            ind.set_active(False)
        self.hist_rpm_full.clear()
        self.hist_curr_full.clear()
        self.hist_volt_full.clear()
        self.hist_temp_motor_full.clear()
        self.hist_temp_ctrl_full.clear()
        self._tick = 0

    def _on_watchdog_disconnect(self):
        """Called from reader thread — schedule UI update on main thread."""
        QTimer.singleShot(0, self._handle_watchdog_disconnect)

    def _handle_watchdog_disconnect(self):
        if not self.backend.conectado:
            return
        self.backend.desconectar()
        self._reset_ui_after_disconnect()
        self.lbl_status.setText("CABO DESCONECTADO")
        self.lbl_status.setStyleSheet(
            "background-color:rgba(255,165,0,0.15); color:#FFA500; padding:8px; font-weight:bold;"
        )
        self.lbl_erro.setText("⚠️ CABO DESCONECTADO")
        self.lbl_erro.setStyleSheet("color:#FFA500;")
        QMessageBox.warning(
            self,
            "Conexão Perdida",
            "O cabo USB foi desconectado ou a controladora parou de responder.\n"
            "Verifique a conexão e clique em 'Ligar' novamente.",
        )

    # ──────────────────────────────────────────────────────────────────
    # Lock / config controls
    # ──────────────────────────────────────────────────────────────────

    def toggle_lock(self):
        unlocking = "Desbloquear" in self.btn_lock.text()
        self.btn_lock.setText("🔓 Bloquear" if unlocking else "🔒 Desbloquear")
        self.btn_lock.setStyleSheet(
            "color:#FF4B4B; border:1px solid #FF4B4B;" if unlocking else ""
        )
        for w in self.widgets_config:
            w.setEnabled(unlocking)

    def carregar_ficheiro_heb(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Backup Fardriver",
            "",
            "Ficheiros Fardriver (*.heb);;Todos (*)",
        )
        if path:
            try:
                dados = HebParser.parse_file(path)
                self.populate_params_tab(dados)
                # Also sync quick sliders
                self.sl_polos.setValue(dados.get("pole_pairs", 4))
                self.sl_linha.setValue(int(dados.get("max_line_curr", 80)))
                self.sl_fase.setValue(int(dados.get("max_phase_curr", 250)))
                self.cb_throttle.setCurrentIndex(dados.get("throttle_response", 0))
                self.cb_weaka.setCurrentIndex(dados.get("weaka", 0))
                QMessageBox.information(
                    self,
                    "HEB Carregado",
                    "Ficheiro lido com sucesso!\nParâmetros preenchidos nas abas.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro", f"Falha ao processar o ficheiro:\n{e}"
                )

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
                self, "Sucesso", "Parâmetros enviados à controladora."
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue o dispositivo primeiro!")

    def gravar_parametros_completos(self):
        """Collect all params_widgets and send via backend."""
        if not self.backend.conectado:
            QMessageBox.warning(self, "Erro", "Ligue o dispositivo primeiro!")
            return
        cfg = {}
        for key, widget in self.params_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                cfg[key] = widget.value()
            elif isinstance(widget, QComboBox):
                cfg[key] = widget.currentIndex()

        # Collect ratio tables
        ratio = {}
        nratio = {}
        for i, lbl in enumerate(RPM_LABELS):
            try:
                ratio[lbl] = int(self.tbl_ratio.item(i, 1).text())
            except Exception:
                ratio[lbl] = 100
            try:
                nratio[f"n{i}"] = int(self.tbl_nratio.item(i, 1).text())
            except Exception:
                nratio[f"n{i}"] = 0
        cfg["ratio_table"] = ratio
        cfg["nratio_table"] = nratio

        if self.backend.enviar_configuracoes(cfg):
            QMessageBox.information(
                self, "Sucesso", "Todos os parâmetros enviados à controladora."
            )
        else:
            QMessageBox.warning(self, "Erro", "Falha ao enviar os parâmetros.")

    def iniciar_autolearn(self):
        if self.backend.iniciar_autolearn():
            QMessageBox.information(
                self,
                "Auto-Aprendizado Iniciado",
                "Comando enviado!\n\nAguarde 2 bipes curtos + 1 longo.\n"
                "Suspenda a roda e acelere ao máximo até o motor parar sozinho.",
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def cancelar_autolearn(self):
        if self.backend.cancelar_autolearn():
            QMessageBox.information(
                self, "Auto-Learn Cancelado", "Comando de cancelamento enviado."
            )
        else:
            QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    def restaurar_fabrica(self):
        resp = QMessageBox.question(
            self,
            "ALERTA — RESTAURAR DE FÁBRICA",
            "⚠️ Todos os parâmetros serão apagados.\nDeseja continuar?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            if self.backend.restaurar_fabrica():
                QMessageBox.information(
                    self, "Restauro Concluído", "Controladora restaurada."
                )
            else:
                QMessageBox.warning(self, "Erro", "Ligue a conexão primeiro!")

    # ──────────────────────────────────────────────────────────────────
    # Params tab helpers
    # ──────────────────────────────────────────────────────────────────

    def populate_params_tab(self, params: dict):
        """Fill all parameter widgets from a dict."""
        mapping = {
            "pole_pairs": ("pole_pairs", lambda w, v: w.setValue(int(v))),
            "rated_speed": ("rated_speed", lambda w, v: w.setValue(int(v))),
            "rated_voltage": ("rated_voltage", lambda w, v: w.setValue(float(v))),
            "rated_power": ("rated_power", lambda w, v: w.setValue(int(v))),
            "max_speed": ("max_speed", lambda w, v: w.setValue(int(v))),
            "phase_offset": ("phase_offset", lambda w, v: w.setValue(float(v))),
            "direction": ("direction", lambda w, v: w.setCurrentIndex(int(v))),
            "throttle_low": ("throttle_low", lambda w, v: w.setValue(float(v))),
            "throttle_high": ("throttle_high", lambda w, v: w.setValue(float(v))),
            "low_vol_protect": ("low_vol_protect", lambda w, v: w.setValue(float(v))),
            "motor_temp_protect": (
                "motor_temp_protect",
                lambda w, v: w.setValue(int(v)),
            ),
            "mos_temp_protect": ("mos_temp_protect", lambda w, v: w.setValue(int(v))),
            "start_ki": ("start_ki", lambda w, v: w.setValue(int(v))),
            "mid_ki": ("mid_ki", lambda w, v: w.setValue(int(v))),
            "max_ki": ("max_ki", lambda w, v: w.setValue(int(v))),
            "start_kp": ("start_kp", lambda w, v: w.setValue(int(v))),
            "mid_kp": ("mid_kp", lambda w, v: w.setValue(int(v))),
            "max_kp": ("max_kp", lambda w, v: w.setValue(int(v))),
        }
        for param_key, (widget_key, setter) in mapping.items():
            if param_key in params and widget_key in self.params_widgets:
                try:
                    setter(self.params_widgets[widget_key], params[param_key])
                except Exception:
                    pass

        # Ratio table
        ratio = params.get("ratio_table", {})
        for i, lbl in enumerate(RPM_LABELS):
            val = ratio.get(lbl)
            if val is not None:
                self.tbl_ratio.setItem(i, 1, QTableWidgetItem(str(val)))

        # nRatio table
        nratio = params.get("nratio_table", {})
        nratio_vals = list(nratio.values())
        for i in range(min(18, len(nratio_vals))):
            self.tbl_nratio.setItem(i, 1, QTableWidgetItem(str(nratio_vals[i])))

        # Firmware info banner
        hw = params.get("hardware_version", "—")
        sw = params.get("software_version", "—")
        self.lbl_fw_info.setText(f"Versão do firmware: {sw} | Hardware: {hw}")

        # Switch PID preset to Personalizado
        self.cb_pid_preset.setCurrentText("Personalizado")

    def _populate_params_from_backend(self):
        params = self.backend.get_params()
        if params:
            self.populate_params_tab(params)

    def _apply_pid_preset(self, name: str):
        preset = PID_PRESETS.get(name)
        if preset is None:
            return
        ski, mki, maxki, skp, mkp, maxkp = preset
        for key, val in [
            ("start_ki", ski),
            ("mid_ki", mki),
            ("max_ki", maxki),
            ("start_kp", skp),
            ("mid_kp", mkp),
            ("max_kp", maxkp),
        ]:
            w = self.params_widgets.get(key)
            if w:
                w.setValue(val)

    # ──────────────────────────────────────────────────────────────────
    # Data collection
    # ──────────────────────────────────────────────────────────────────

    def _iniciar_coleta(self):
        if not self.backend.conectado:
            QMessageBox.warning(self, "Erro", "Ligue o dispositivo primeiro!")
            return
        self.backend.iniciar_coleta_dados()
        QMessageBox.information(
            self,
            "Coleta Iniciada",
            "2048 amostras estão sendo gravadas na flash.\n"
            "Acelere ao máximo por ~20 segundos.\n\n"
            "Os dados serão exibidos assim que chegarem.",
        )

    # ──────────────────────────────────────────────────────────────────
    # Error log
    # ──────────────────────────────────────────────────────────────────

    def _update_error_log(self):
        history = self.backend.error_history
        self.lst_erros.clear()
        for entry in reversed(history):
            text = f"[{entry['time']}]  Erro {entry['code']:02d}  —  {entry['desc']}"
            item = QListWidgetItem(text)
            if entry["code"] != 0:
                item.setForeground(Qt.red)
            self.lst_erros.addItem(item)

    def _limpar_historico_erros(self):
        self.backend.error_history.clear()
        self.backend._last_error_code = 0
        self.lst_erros.clear()

    # ──────────────────────────────────────────────────────────────────
    # Export
    # ──────────────────────────────────────────────────────────────────

    def exportar_csv(self):
        if not self.hist_rpm_full:
            QMessageBox.warning(
                self, "Sem Dados", "Não há dados gravados para exportar."
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar CSV",
            f"Dados_Leviata_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
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
                    "Temp_Motor_C",
                    "Temp_Ctrl_C",
                ]
            )
            n = len(self.hist_rpm_full)
            for i in range(n):
                writer.writerow(
                    [
                        i,
                        self.hist_rpm_full[i],
                        self.hist_curr_full[i],
                        self.hist_volt_full[i],
                        self.hist_temp_motor_full[i]
                        if i < len(self.hist_temp_motor_full)
                        else "",
                        self.hist_temp_ctrl_full[i]
                        if i < len(self.hist_temp_ctrl_full)
                        else "",
                    ]
                )
        QMessageBox.information(self, "CSV Exportado", f"Arquivo salvo:\n{path}")

    def salvar_perfil(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Perfil de Configuração",
            f"Perfil_Leviata_{datetime.now().strftime('%Y%m%d')}.json",
            "JSON (*.json)",
        )
        if not path:
            return
        profile = {}
        for key, widget in self.params_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                profile[key] = widget.value()
            elif isinstance(widget, QComboBox):
                profile[key] = widget.currentIndex()
        ratio = {}
        nratio = {}
        for i, lbl in enumerate(RPM_LABELS):
            try:
                ratio[lbl] = int(self.tbl_ratio.item(i, 1).text())
            except Exception:
                ratio[lbl] = 100
            try:
                nratio[f"n{i}"] = int(self.tbl_nratio.item(i, 1).text())
            except Exception:
                nratio[f"n{i}"] = 0
        profile["ratio_table"] = ratio
        profile["nratio_table"] = nratio
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "Perfil Salvo", f"Perfil salvo em:\n{path}")

    def carregar_perfil(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Carregar Perfil de Configuração", "", "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            self.populate_params_tab(profile)
            QMessageBox.information(
                self, "Perfil Carregado", "Configurações carregadas com sucesso!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar perfil:\n{e}")

    # ──────────────────────────────────────────────────────────────────
    # Report
    # ──────────────────────────────────────────────────────────────────

    def gerar_relatorio_html(self):
        if not self.hist_rpm_full:
            QMessageBox.warning(
                self, "Sem Dados", "Ligue a controladora e aguarde dados chegarem."
            )
            return
        t = self.backend.ler_dados()
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Relatório",
            f"Relatorio_Leviata_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            "HTML (*.html)",
        )
        if not path:
            return
        STEP = max(1, len(self.hist_rpm_full) // 3000)
        caminho = ReportGenerator.generate_html_report(
            t,
            self.hist_rpm_full[::STEP],
            self.hist_curr_full[::STEP],
            self.hist_volt_full[::STEP],
            list(range(len(self.hist_rpm_full[::STEP]))),
            os.path.dirname(path),
            self.hist_temp_motor_full[::STEP],
            self.hist_temp_ctrl_full[::STEP],
        )
        if caminho and os.path.isfile(caminho) and caminho != path:
            os.replace(caminho, path)

    # ──────────────────────────────────────────────────────────────────
    # Telemetry update loop (100 ms)
    # ──────────────────────────────────────────────────────────────────

    def update_telemetry_loop(self):
        t = self.backend.ler_dados()

        # Cards row 1
        self.card_rpm.update_data(t["rpm"], t["rpm"] - self.prev_telemetry["rpm"])
        self.card_volt.update_data(t["volt"], t["volt"] - self.prev_telemetry["volt"])
        self.card_curr.update_data(
            t["curr"], t["curr"] - self.prev_telemetry["curr"], True
        )
        self.card_power.update_data(
            t["power"], t["power"] - self.prev_telemetry["power"], True
        )
        self.card_soc.update_data(t.get("batt_soc", 0), 0)

        # Cards row 2
        self.card_torque.update_data(
            t["torque"], t["torque"] - self.prev_telemetry.get("torque", 0), True
        )
        self.card_temp.update_data(t["temp_motor"], 0, True)
        self.card_temp_ctrl.update_data(t["temp_mosfet"], 0, True)
        self.card_throttle.update_data(t["throttle"], 0)
        self.card_phase_off.update_data(t.get("phase_offset", 0.0), 0)

        # Temperature alerts
        self.card_temp.set_alert(t["temp_motor"] > 80)
        self.card_temp_ctrl.set_alert(t["temp_mosfet"] > 70)

        # Hall + status indicators
        self.hall_widget.update_state(t["hall_a"], t["hall_b"], t["hall_c"])
        self.ind_forward.set_active(t.get("forward", False))
        self.ind_reverse.set_active(t.get("reverse", False))
        self.ind_brake.set_active(t.get("brake", False))
        self.ind_motion.set_active(t.get("motion", False))

        # Error label
        err = t["error"]
        if err != 0:
            from fardriver_serial import ERROS_FARDRIVER

            desc = ERROS_FARDRIVER.get(err, f"Erro {err}")
            self.lbl_erro.setText(f"⚠️ {desc}")
            self.lbl_erro.setStyleSheet("color:#FF4B4B;")
        else:
            self.lbl_erro.setText("SISTEMA OK")
            self.lbl_erro.setStyleSheet("color:#00FF00;")

        self.prev_telemetry = t.copy()

        # History
        self.hist_rpm_full.append(t["rpm"])
        self.hist_curr_full.append(t["curr"])
        self.hist_volt_full.append(t["volt"])
        self.hist_temp_motor_full.append(t["temp_motor"])
        self.hist_temp_ctrl_full.append(t["temp_mosfet"])

        # Charts (sliding window)
        self._tick += 1
        n = min(self._tick, self.max_pts_tela)
        x = list(range(self._tick - n, self._tick))
        self.l_rpm.setData(x, self.hist_rpm_full[-n:])
        self.l_curr.setData(x, self.hist_curr_full[-n:])
        self.l_volt.setData(x, self.hist_volt_full[-n:])

        # Error log every 30 ticks
        if self._tick % 30 == 0:
            self._update_error_log()


# ==============================================================================
# Entry point
# ==============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    window = FardriverApp()
    window.show()
    sys.exit(app.exec_())
