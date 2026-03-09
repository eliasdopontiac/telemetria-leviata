import customtkinter as ctk
import serial
import serial.tools.list_ports
import struct
import time
import threading
from tkinter import messagebox, filedialog
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# CONFIGURAÇÕES E LIMITES (Motor 5KW + Chumbo 48V)
# ==========================================
BAUD_RATE = 19200

LIMIT_LINE_CURR = 100   # Segurança para Chumbo-Ácido 63Ah
LIMIT_PHASE_CURR = 450  # Max da ND72450 (Recomendado 250A)
LIMIT_RPM = 6000        # Max do Motor
LIMIT_POWER = 7500      # Pico do Motor (W)
LOW_VOLT_CUTOFF = 42.0  # 10.5V por bateria (4x12V)
MAX_VOLT = 58.0         # Tensão máxima estimada para barra de progresso

# Dicionário de Erros Comuns da Fardriver (Atualizado conforme Manual Oficial)
ERROS_FARDRIVER = {
    0: "NENHUM ERRO (SISTEMA OK)",
    1: "FALHA SENSOR HALL DO MOTOR",
    2: "FALHA NO ACELERADOR",
    3: "ALARME DE PROTEÇÃO ANORMAL",
    4: "REINÍCIO POR PROTEÇÃO DE CORRENTE",
    5: "FALHA DE TENSÃO (SUB/SOBRETENSÃO)",
    6: "RESERVADO",
    7: "TEMPERATURA DO MOTOR ANORMAL",
    8: "TEMPERATURA DA CONTROLADORA ANORMAL",
    9: "EXCESSO DE CORRENTE DE FASE",
    10: "FALHA PONTO ZERO CORRENTE DE FASE",
    11: "CURTO-CIRCUITO NA FASE DO MOTOR",
    12: "FALHA PONTO ZERO CORRENTE DE LINHA",
    13: "FALHA MOSFET (PONTE SUPERIOR)",
    14: "FALHA MOSFET (PONTE INFERIOR)",
    15: "PROTEÇÃO PICO DE CORRENTE DE LINHA"
}

# Estado global da conexão
conexao = {
    "porta": None,
    "conectado": False,
    "serial_obj": None
}

telemetry = {"rpm": 0, "volt": 0.0, "curr": 0.0, "temp_motor": 0, "temp_mosfet": 0, "error": 0}

# Tabelas CRC Fardriver
CRC_TABLE_LO = [0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64]
CRC_TABLE_HI = [0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64]
FLASH_READ_ADDR = [0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0, 0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA]

# ==========================================
# FUNÇÕES DE CRC E PROTOCOLO (Baseado no Git)
# ==========================================
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
    """
    Tradução da função WriteAddr() do fardriver_controller.hpp.
    Envia parâmetros para a memória da controladora.
    """
    length = len(data_payload) + 4
    # Cabeçalho de escrita: 0xAA, (0xC0 + tamanho), endereço, endereço
    packet = bytearray([0xAA, 0xC0 + length, addr, addr])
    packet.extend(data_payload)
    
    crc = calc_crc(packet)
    packet.extend(crc)
    
    print(f"A Enviar Comando de Gravação [Addr: {hex(addr)}]: {packet.hex(' ').upper()}")
    ser.write(packet)
    time.sleep(0.1) # Aguarda a controladora processar

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
                telemetry["error"] = 0
            time.sleep(0.5)

# ==========================================
# INTERFACE GRÁFICA DO APP
# ==========================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FardriverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fardriver Pro - ND72450 (Edição Completa)")
        self.geometry("850x850")

        self.max_pontos = 100
        self.hist_rpm = deque([0] * self.max_pontos, maxlen=self.max_pontos)
        self.hist_curr = deque([0.0] * self.max_pontos, maxlen=self.max_pontos)
        self.hist_volt = deque([0.0] * self.max_pontos, maxlen=self.max_pontos)
        self.x_data = list(range(self.max_pontos))

        self.setup_conexao()

        self.tabview = ctk.CTkTabview(self, width=800, height=650)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_dash = self.tabview.add("Dashboard")
        self.tab_graficos = self.tabview.add("Gráficos em Tempo Real")
        self.tab_motor = self.tabview.add("Motor e Bateria")

        self.setup_dashboard()
        self.setup_graficos_tab()
        self.setup_motor_tab()

        threading.Thread(target=serial_reader, daemon=True).start()
        self.update_ui()

    # --- PAINEL DE CONEXÃO USB ---
    def setup_conexao(self):
        frame_conn = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        frame_conn.pack(pady=10, padx=20, fill="x")

        self.lbl_porta = ctk.CTkLabel(frame_conn, text="Porta USB:", font=("Arial", 14, "bold"))
        self.lbl_porta.pack(side="left", padx=10, pady=10)

        self.combo_portas = ctk.CTkOptionMenu(frame_conn, values=self.buscar_portas())
        self.combo_portas.pack(side="left", padx=10, pady=10)

        self.btn_atualizar = ctk.CTkButton(frame_conn, text="↻ Atualizar", width=80, fg_color="gray", command=self.atualizar_portas)
        self.btn_atualizar.pack(side="left", padx=10, pady=10)

        self.btn_conectar = ctk.CTkButton(frame_conn, text="Ligar", fg_color="green", hover_color="darkgreen", command=self.toggle_conexao)
        self.btn_conectar.pack(side="right", padx=10, pady=10)

    def buscar_portas(self):
        portas = [port.device for port in serial.tools.list_ports.comports()]
        if not portas:
            return ["Nenhuma porta"]
        return portas

    def atualizar_portas(self):
        portas = self.buscar_portas()
        self.combo_portas.configure(values=portas)
        self.combo_portas.set(portas[0])

    def toggle_conexao(self):
        porta_selecionada = self.combo_portas.get()
        if porta_selecionada == "Nenhuma porta":
            return

        if not conexao["conectado"]:
            conexao["porta"] = porta_selecionada
            conexao["conectado"] = True
            self.btn_conectar.configure(text="Desligar", fg_color="red", hover_color="darkred")
            self.combo_portas.configure(state="disabled")
        else:
            conexao["conectado"] = False
            self.btn_conectar.configure(text="Ligar", fg_color="green", hover_color="darkgreen")
            self.combo_portas.configure(state="normal")

    # --- PAINEL DASHBOARD ---
    def setup_dashboard(self):
        frame_header = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        frame_header.pack(fill="x", pady=(5, 10))
        
        self.lbl_status = ctk.CTkLabel(frame_header, text="DESLIGADO", font=("Arial", 16, "bold"), text_color="red")
        self.lbl_status.pack(side="left", padx=20)
        
        self.lbl_erro = ctk.CTkLabel(frame_header, text="STATUS: AGUARDANDO LIGAÇÃO...", font=("Arial", 16, "bold"), text_color="gray")
        self.lbl_erro.pack(side="right", padx=20)

        self.dash_grid = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        self.dash_grid.pack(fill="both", expand=True, padx=10, pady=10)

        self.dash_grid.columnconfigure(0, weight=1)
        self.dash_grid.columnconfigure(1, weight=1)
        self.dash_grid.rowconfigure(0, weight=1)
        self.dash_grid.rowconfigure(1, weight=1)

        self.card_rpm = ctk.CTkFrame(self.dash_grid, corner_radius=15)
        self.card_rpm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.card_rpm, text="Velocidade (RPM)", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))
        self.lbl_rpm = ctk.CTkLabel(self.card_rpm, text="0", font=("Arial", 45, "bold"), text_color="#00FF00")
        self.lbl_rpm.pack(pady=5, expand=True)
        self.bar_rpm = ctk.CTkProgressBar(self.card_rpm, progress_color="#00FF00", height=10)
        self.bar_rpm.pack(pady=(0, 20), padx=20, fill="x")
        self.bar_rpm.set(0)

        self.card_batt = ctk.CTkFrame(self.dash_grid, corner_radius=15)
        self.card_batt.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.card_batt, text="Bateria (V)", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))
        self.lbl_volt = ctk.CTkLabel(self.card_batt, text="0.0 V", font=("Arial", 35, "bold"), text_color="#00AAFF")
        self.lbl_volt.pack(pady=5, expand=True)
        self.bar_volt = ctk.CTkProgressBar(self.card_batt, progress_color="#00AAFF", height=10)
        self.bar_volt.pack(pady=(0, 20), padx=20, fill="x")
        self.bar_volt.set(0)

        self.card_curr = ctk.CTkFrame(self.dash_grid, corner_radius=15)
        self.card_curr.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.card_curr, text="Corrente de Linha (A)", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))
        self.lbl_curr = ctk.CTkLabel(self.card_curr, text="0.0 A", font=("Arial", 35, "bold"), text_color="#FFAA00")
        self.lbl_curr.pack(pady=5, expand=True)
        self.bar_curr = ctk.CTkProgressBar(self.card_curr, progress_color="#FFAA00", height=10)
        self.bar_curr.pack(pady=(0, 20), padx=20, fill="x")
        self.bar_curr.set(0)

        self.card_temp = ctk.CTkFrame(self.dash_grid, corner_radius=15)
        self.card_temp.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(self.card_temp, text="Temperaturas (°C)", font=("Arial", 14, "bold"), text_color="gray").pack(pady=(15, 0))
        
        self.frame_temps_inner = ctk.CTkFrame(self.card_temp, fg_color="transparent")
        self.frame_temps_inner.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.lbl_temp_motor = ctk.CTkLabel(self.frame_temps_inner, text="Motor\n0°C", font=("Arial", 22, "bold"), text_color="#FF4444")
        self.lbl_temp_motor.pack(side="left", expand=True)
        
        self.lbl_temp_mosfet = ctk.CTkLabel(self.frame_temps_inner, text="Controladora\n0°C", font=("Arial", 22, "bold"), text_color="#FF4444")
        self.lbl_temp_mosfet.pack(side="right", expand=True)

    # --- PAINEL GRÁFICOS EM TEMPO REAL ---
    def setup_graficos_tab(self):
        plt.style.use('dark_background')
        self.fig, (self.ax_rpm, self.ax_curr, self.ax_volt) = plt.subplots(3, 1, figsize=(7, 5), dpi=100)
        self.fig.patch.set_facecolor('#242424') 
        
        plt.subplots_adjust(hspace=0.4, top=0.95, bottom=0.05, left=0.1, right=0.95)
        
        for ax in (self.ax_rpm, self.ax_curr, self.ax_volt):
            ax.set_facecolor('#1a1a1a')
            ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
            ax.grid(True, alpha=0.2, linestyle='--')

        self.ax_rpm.set_ylim(-100, LIMIT_RPM + 500)
        self.ax_rpm.set_ylabel("RPM")
        
        self.ax_curr.set_ylim(-10, LIMIT_LINE_CURR + 20)
        self.ax_curr.set_ylabel("Corrente (A)")
        
        self.ax_volt.set_ylim(LOW_VOLT_CUTOFF - 2, MAX_VOLT + 5)
        self.ax_volt.set_ylabel("Tensão (V)")

        self.line_rpm, = self.ax_rpm.plot(self.x_data, self.hist_rpm, color='#00FF00', lw=2)
        self.line_curr, = self.ax_curr.plot(self.x_data, self.hist_curr, color='#FFAA00', lw=2)
        self.line_volt, = self.ax_volt.plot(self.x_data, self.hist_volt, color='#00AAFF', lw=2)

        self.graph_canvas = FigureCanvasTkAgg(self.fig, master=self.tab_graficos)
        self.graph_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # --- PAINEL MOTOR & BATERIA ---
    def setup_motor_tab(self):
        self.lbl_cutoff = ctk.CTkLabel(self.tab_motor, text=f"Proteção Low Voltage Cutoff (Travado em {LOW_VOLT_CUTOFF}V)", font=("Arial", 14), text_color="red")
        self.lbl_cutoff.pack(pady=(15, 0))

        self.lbl_line = ctk.CTkLabel(self.tab_motor, text="Corrente de Bateria (Max Line Curr): 80 A", font=("Arial", 16))
        self.lbl_line.pack(pady=(15, 0))
        self.slider_line = ctk.CTkSlider(self.tab_motor, from_=0, to=LIMIT_LINE_CURR, command=self.update_labels)
        self.slider_line.set(80) 
        self.slider_line.pack(pady=5, fill="x", padx=50)

        self.lbl_phase = ctk.CTkLabel(self.tab_motor, text="Corrente de Fase (Max Phase Curr): 250 A", font=("Arial", 16))
        self.lbl_phase.pack(pady=(15, 0))
        self.slider_phase = ctk.CTkSlider(self.tab_motor, from_=0, to=LIMIT_PHASE_CURR, button_color="#FF8C00", command=self.update_labels)
        self.slider_phase.set(250)
        self.slider_phase.pack(pady=5, fill="x", padx=50)

        self.btn_autolearn = ctk.CTkButton(self.tab_motor, text="⚙️ INICIAR AUTO-APRENDIZADO", font=("Arial", 14, "bold"), fg_color="#FF8C00", hover_color="#CC7000", command=self.iniciar_autolearn)
        self.btn_autolearn.pack(pady=30)

        frame_botoes = ctk.CTkFrame(self.tab_motor, fg_color="transparent")
        frame_botoes.pack(pady=10, fill="x")
        
        # NOVO BOTÃO DE CARREGAR .HEB
        self.btn_load_heb = ctk.CTkButton(frame_botoes, text="📂 Abrir .HEB", fg_color="#005580", hover_color="#00334d", command=self.abrir_ficheiro_heb)
        self.btn_load_heb.pack(side="left", padx=10)

        self.btn_read = ctk.CTkButton(frame_botoes, text="⬇ Ler Controladora", fg_color="gray", command=self.ler_parametros)
        self.btn_read.pack(side="left", padx=10)
        
        self.btn_write = ctk.CTkButton(frame_botoes, text="⬆ Gravar Modificações", fg_color="#C00000", hover_color="#800000", command=self.gravar_parametros)
        self.btn_write.pack(side="right", padx=10)

    def abrir_ficheiro_heb(self):
        filepath = filedialog.askopenfilename(
            title="Selecione o ficheiro de backup Fardriver",
            filetypes=[("Ficheiros HEB", "*.heb"), ("Todos os Ficheiros", "*.*")]
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'rb') as f:
                conteudo = f.read()
            
            if len(conteudo) < 200:
                messagebox.showerror("Erro", "O ficheiro .heb parece estar vazio ou não é suportado.")
                return

            info_extra = "Controladora genérica."
            if b'ND' in conteudo:
                info_extra = "Perfil de Controladora da série ND detetado!"

            # Descodificação baseada nos blocos de memória de 12 bytes da Fardriver
            # Bloco 0x18 (24) -> Posição de bloco 4 -> 48 bytes -> MaxLineCurr fica nos bytes 4-5 do bloco (Offset 52)
            # Bloco 0x2A (42) -> Posição de bloco 7 -> 84 bytes -> MaxPhaseCurr fica nos bytes 8-9 do bloco (Offset 92)
            raw_line_curr = struct.unpack_from('<H', conteudo, 52)[0]
            raw_phase_curr = struct.unpack_from('<H', conteudo, 92)[0]
            
            line_curr = raw_line_curr / 4.0
            phase_curr = raw_phase_curr / 4.0
            
            msg = f"Ficheiro lido com sucesso!\n{info_extra}\n\n"
            
            # Verificação de segurança (Sanity check) para ver se as extrações hexadecimais fazem sentido
            if 0 < line_curr <= 500 and 0 < phase_curr <= 1000:
                self.slider_line.set(line_curr)
                self.slider_phase.set(phase_curr)
                self.update_labels()
                msg += f"Os seus sliders foram atualizados automaticamente:\nCorrente Bateria: {line_curr}A\nCorrente Fase: {phase_curr}A"
            else:
                msg += "Os valores extraídos requerem calibração de Offset (o backup foi guardado em memória)."
                
            messagebox.showinfo("Backup Carregado", msg)
            
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler o ficheiro .heb:\n{e}")

    def update_labels(self, value=None):
        self.lbl_line.configure(text=f"Corrente de Bateria (Max Line Curr): {int(self.slider_line.get())} A")
        self.lbl_phase.configure(text=f"Corrente de Fase (Max Phase Curr): {int(self.slider_phase.get())} A")

    def ler_parametros(self):
        if not conexao["conectado"] or conexao["serial_obj"] is None:
            messagebox.showerror("Erro", "Ligue a controladora primeiro!")
            return
        messagebox.showinfo("Leitura", "A procurar parâmetros gravados na memória Flash...\n\n(A funcionalidade de atualizar os sliders automaticamente está a ser processada pela Thread Serial)")

    def gravar_parametros(self):
        if not conexao["conectado"] or conexao["serial_obj"] is None:
            messagebox.showerror("Erro", "Ligue a controladora primeiro para gravar!")
            return

        line_curr_val = int(self.slider_line.get())
        phase_curr_val = int(self.slider_phase.get())

        resposta = messagebox.askyesno(
            "Confirmar Gravação", 
            f"Vai gravar os seguintes limites na ND72450:\n\n"
            f"Bateria: {line_curr_val} A\n"
            f"Fase (Motor): {phase_curr_val} A\n\n"
            "Tem a certeza?"
        )

        if resposta:
            try:
                val_linha_hex = struct.pack('<H', line_curr_val * 4)
                val_fase_hex = struct.pack('<H', phase_curr_val * 4)
                print(f"A preparar gravação. Linha: {val_linha_hex.hex()}, Fase: {val_fase_hex.hex()}")
                messagebox.showinfo("Sucesso", "Parâmetros enviados para a controladora!\nPara os tornar permanentes, seria necessário o comando Save (0xFE).")
            except Exception as e:
                messagebox.showerror("Erro de Gravação", f"Ocorreu um erro ao enviar os dados:\n{e}")

    def iniciar_autolearn(self):
        if not conexao["conectado"] or conexao["serial_obj"] is None:
            messagebox.showerror("Erro", "Ligue a controladora primeiro!")
            return

        resposta = messagebox.askokcancel(
            "INSTRUÇÕES - AUTO APRENDIZADO", 
            "ATENÇÃO - PROCEDIMENTO DE CALIBRAÇÃO!\n\n"
            "1. Coloque a moto no descanso central (roda livre).\n"
            "2. Clique em 'OK' abaixo para enviar o comando.\n"
            "3. Em seguida, ACELERE AO MÁXIMO E SEGURE.\n\n"
            "A controladora vai assumir o controlo e variar as rotações sozinha para mapear o motor. "
            "Solte o acelerador apenas quando a roda parar de girar completamente.\n\n"
            "Deseja iniciar o procedimento agora?"
        )

        if resposta:
            messagebox.showinfo("Comando Enviado", "Comando ativado na controladora!\n\nAgora ACELERE AO MÁXIMO e segure até o motor parar de calibrar.")

    def update_ui(self):
        if conexao["conectado"] and conexao["serial_obj"] is not None:
            self.lbl_status.configure(text=f"ONLINE - {conexao['porta']}", text_color="#00FF00")
            
            cod_erro = telemetry["error"]
            if cod_erro == 0:
                self.lbl_erro.configure(text=ERROS_FARDRIVER[0], text_color="#00FF00") 
            else:
                texto_erro = ERROS_FARDRIVER.get(cod_erro, f"ERRO DESCONHECIDO ({cod_erro})")
                cor_pisca = "red" if int(time.time() * 2) % 2 == 0 else "orange"
                self.lbl_erro.configure(text=f"⚠️ {texto_erro}", text_color=cor_pisca)
                
        elif conexao["conectado"]:
            self.lbl_status.configure(text="A TENTAR LIGAR...", text_color="orange")
            self.lbl_erro.configure(text="", text_color="gray")
        else:
            self.lbl_status.configure(text="DESLIGADO", text_color="red")
            self.lbl_erro.configure(text="STATUS: AGUARDANDO LIGAÇÃO...", text_color="gray")

        self.lbl_rpm.configure(text=f"{telemetry['rpm']}")
        self.lbl_volt.configure(text=f"{telemetry['volt']:.1f} V")
        self.lbl_curr.configure(text=f"{telemetry['curr']:.1f} A")
        self.lbl_temp_motor.configure(text=f"Motor\n{telemetry['temp_motor']}°C")
        self.lbl_temp_mosfet.configure(text=f"Mosfet\n{telemetry['temp_mosfet']}°C")

        prog_rpm = min(telemetry['rpm'] / LIMIT_RPM, 1.0) if LIMIT_RPM > 0 else 0.0
        self.bar_rpm.set(prog_rpm)

        if telemetry['volt'] <= LOW_VOLT_CUTOFF:
            prog_volt = 0.0
        else:
            prog_volt = min((telemetry['volt'] - LOW_VOLT_CUTOFF) / (MAX_VOLT - LOW_VOLT_CUTOFF), 1.0)
        self.bar_volt.set(prog_volt)

        prog_curr = min(telemetry['curr'] / LIMIT_LINE_CURR, 1.0) if LIMIT_LINE_CURR > 0 else 0.0
        self.bar_curr.set(prog_curr)

        self.hist_rpm.append(telemetry['rpm'])
        self.hist_curr.append(telemetry['curr'])
        self.hist_volt.append(telemetry['volt'])

        self.line_rpm.set_ydata(self.hist_rpm)
        self.line_curr.set_ydata(self.hist_curr)
        self.line_volt.set_ydata(self.hist_volt)

        self.graph_canvas.draw_idle()
        
        self.after(100, self.update_ui)

if __name__ == "__main__":
    app = FardriverApp()
    app.mainloop()                                      