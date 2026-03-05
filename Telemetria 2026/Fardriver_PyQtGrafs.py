import sys
import serial
import struct
import time
import threading
from collections import deque
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer

# ==========================================
# CONFIGURAÇÕES DA SERIAL
# ==========================================
SERIAL_PORT = 'COM5'
BAUD_RATE = 19200
MAX_POINTS = 200  # PyQtGraph é rápido, podemos dobrar os pontos!

# Tabelas CRC (Originais do Fardriver)
CRC_TABLE_LO = [0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64]
CRC_TABLE_HI = [0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64]
FLASH_READ_ADDR = [0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0, 0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA]

# ==========================================
# BUFFERS E LÓGICA SERIAL
# ==========================================
rpm_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
current_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
voltage_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
last_values = {"rpm": 0, "volt": 0.0, "curr": 0.0, "temp_motor": 0, "temp_mosfet": 0}

def check_crc(header_byte, data_bytes, crc_bytes):
    a, b = 0x3C, 0x7F
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    for byte in full_msg:
        crc_i = a ^ byte
        a, b = b ^ CRC_TABLE_HI[crc_i], CRC_TABLE_LO[crc_i]
    return crc_bytes[0] == a and crc_bytes[1] == b

def send_keep_alive(ser):
    try: ser.write(bytes([0xAA, 0x13, 0xEC, 0x07, 0x01, 0xF1, 0x48, 0xB7]))
    except: pass

def serial_reader():
    try: ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    except Exception as e: return print(f"Erro ao abrir serial: {e}")

    send_keep_alive(ser)
    last_ka = time.time()
    buffer = b''

    while True:
        if time.time() - last_ka > 1.0:
            send_keep_alive(ser)
            last_ka = time.time()

        try:
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
                            v = struct.unpack_from('<h', data, 0)[0] / 10.0
                            c = struct.unpack_from('<h', data, 4)[0] / 4.0
                            voltage_data.append(v)
                            current_data.append(c)
                            last_values["volt"] = v
                            last_values["curr"] = c
                        elif addr == 0xE2:
                            raw_rpm = struct.unpack_from('<h', data, 6)[0]
                            rpm_real = abs(raw_rpm) if abs(raw_rpm) >= 20 else 0
                            rpm_data.append(rpm_real)
                            last_values["rpm"] = rpm_real
                        elif addr == 0xF4:
                            last_values["temp_motor"] = struct.unpack_from('<h', data, 0)[0]
                        elif addr == 0xD6:
                            last_values["temp_mosfet"] = struct.unpack_from('<h', data, 10)[0]
                    buffer = buffer[16:]
                else:
                    buffer = buffer[1:]
            time.sleep(0.01)
        except Exception: break

# ==========================================
# INTERFACE GRÁFICA (PyQtGraph)
# ==========================================
class TelemetryDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fardriver Pro Telemetry")
        self.resize(1000, 800)

        # Widget Principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Painel Superior (Textos Grandes)
        self.label_info = QLabel("INICIALIZANDO...")
        self.label_info.setStyleSheet("font-size: 24px; font-weight: bold; color: #00FFcc; background-color: #111; padding: 10px;")
        layout.addWidget(self.label_info)

        # Configuração PyQtGraph
        pg.setConfigOptions(antialias=True)
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        # Gráfico RPM
        self.plot_rpm = self.graph_widget.addPlot(title="RPM do Motor")
        self.plot_rpm.showGrid(x=True, y=True, alpha=0.3)
        self.curve_rpm = self.plot_rpm.plot(pen=pg.mkPen('#00FF00', width=2))
        
        self.graph_widget.nextRow()
        
        # Gráfico Corrente
        self.plot_curr = self.graph_widget.addPlot(title="Corrente de Linha (A)")
        self.plot_curr.showGrid(x=True, y=True, alpha=0.3)
        self.curve_curr = self.plot_curr.plot(pen=pg.mkPen('#FFAA00', width=2))

        self.graph_widget.nextRow()

        # Gráfico Tensão
        self.plot_volt = self.graph_widget.addPlot(title="Tensão Bateria (V)")
        self.plot_volt.showGrid(x=True, y=True, alpha=0.3)
        self.curve_volt = self.plot_volt.plot(pen=pg.mkPen('#00AAFF', width=2))

        # Timer para atualizar a tela a 30 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(30)

    def update_gui(self):
        # Atualiza as linhas
        self.curve_rpm.setData(list(rpm_data))
        self.curve_curr.setData(list(current_data))
        self.curve_volt.setData(list(voltage_data))

        # Atualiza os textos
        info_text = (f"⚡ VOLT: {last_values['volt']:.1f} V    |    "
                     f"🔋 CORRENTE: {last_values['curr']:.1f} A    |    "
                     f"🚀 RPM: {last_values['rpm']}    |    "
                     f"🔥 MOTOR: {last_values['temp_motor']}°C    |    "
                     f"🛠️ MOSFET: {last_values['temp_mosfet']}°C")
        self.label_info.setText(info_text)

if __name__ == '__main__':
    # Inicia a leitura da serial em paralelo
    threading.Thread(target=serial_reader, daemon=True).start()

    # Inicia a Interface
    app = QApplication(sys.argv)
    app.setStyle('Fusion') # Estilo mais moderno
    window = TelemetryDashboard()
    window.show()
    sys.exit(app.exec_())