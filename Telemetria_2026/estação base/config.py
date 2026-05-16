import flet as ft

SERIAL_PORT = "COM3"
BAUD_RATE = 9600
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "barco/telemetria/+"
CSV_FILE = "telemetria_solar.csv"
MAX_VEL_HISTORY = 200
POT_MAX = 600

# Dados do Barco para Autonomia
BAT_CAPACITY_AH = 40.0  # Capacidade total em Ah
BAT_VOLTAGE_NOMINAL = 48.0 # Tensão nominal do sistema

# Paleta de Cores Premium
BG_COLOR = "#09090b"
CARD_COLOR = "#121214"
BORDER_COLOR = "#27272a"
PRIMARY = "#06b6d4"
PRIMARY_MUTED = "#164e63"
FG = "#fafafa"
MUTED = "#a1a1aa"

# Cores Semânticas
AMBER = "#f59e0b"
GREEN = "#22c55e"
RED = "#ef4444"
YELLOW = "#eab308"
BLUE = "#3b82f6"
SUCCESS = "#10b981"


