import serial
import struct
import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# ==========================================
# CONFIGURAÇÕES
# ==========================================
SERIAL_PORT = 'COM5'   # Altere para a sua porta
BAUD_RATE = 19200
MAX_POINTS = 100       # Quantidade de pontos no gráfico (janela de tempo)

# Tabelas CRC (Originais do fardriver_message.hpp)
CRC_TABLE_LO = [0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64]
CRC_TABLE_HI = [0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64]
FLASH_READ_ADDR = [0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0, 0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA]

# Buffers de dados para o gráfico (Filas que removem o mais antigo quando enchem)
rpm_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
current_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)
voltage_data = deque([0] * MAX_POINTS, maxlen=MAX_POINTS)

# Dicionário para atualizar os textos rapidamente
last_values = {"rpm": 0, "volt": 0.0, "curr": 0.0, "temp_motor": 0, "temp_mosfet": 0}

def check_crc(header_byte, data_bytes, crc_bytes):
    a = 0x3C
    b = 0x7F
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    for byte in full_msg:
        crc_i = a ^ byte
        a = b ^ CRC_TABLE_HI[crc_i]
        b = CRC_TABLE_LO[crc_i]
    return crc_bytes[0] == a and crc_bytes[1] == b

def send_keep_alive(ser):
    cmd_packet = bytes([0xAA, 0x13, 0xEC, 0x07, 0x01, 0xF1, 0x48, 0xB7])
    try:
        ser.write(cmd_packet)
    except:
        pass

# ==========================================
# THREAD DE LEITURA DA PORTA SERIAL
# ==========================================
def serial_reader():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"Conectado em {SERIAL_PORT}")
    except Exception as e:
        print(f"Erro ao abrir serial: {e}")
        return

    send_keep_alive(ser)
    last_ka = time.time()
    buffer = b''

    while True:
        # Keep Alive a cada 1 segundo
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
                header = pkt[1]
                data = pkt[2:14]
                crc = pkt[14:16]
                
                if check_crc(header, data, crc):
                    pkt_id = header & 0x3F
                    if pkt_id < len(FLASH_READ_ADDR):
                        addr = FLASH_READ_ADDR[pkt_id]
                        
                        # --- PARSING DOS DADOS ---
                        if addr == 0xE8: # Voltagem e Corrente
                            v = struct.unpack_from('<h', data, 0)[0] / 10.0
                            c = struct.unpack_from('<h', data, 4)[0] / 4.0
                            voltage_data.append(v)
                            current_data.append(c)
                            last_values["volt"] = v
                            last_values["curr"] = c
                            
                        elif addr == 0xE2: # RPM (Corrigido para byte 6)
                            raw_rpm = struct.unpack_from('<h', data, 6)[0]
                            rpm_real = abs(raw_rpm)
                            if rpm_real < 20:
                                rpm_real = 0
                            rpm_data.append(rpm_real)
                            last_values["rpm"] = rpm_real
                            
                        elif addr == 0xF4: # Temp Motor
                            last_values["temp_motor"] = struct.unpack_from('<h', data, 0)[0]
                            
                        elif addr == 0xD6: # Temp Mosfet
                            last_values["temp_mosfet"] = struct.unpack_from('<h', data, 10)[0]

                    buffer = buffer[16:]
                else:
                    buffer = buffer[1:]
            time.sleep(0.01)
        except Exception as e:
            print(f"Erro na serial: {e}")
            break

# ==========================================
# CONFIGURAÇÃO DO GRÁFICO (MATPLOTLIB)
# ==========================================
# Estilo escuro para parecer um painel real
plt.style.use('dark_background')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(10, 8))
fig.canvas.manager.set_window_title('Painel de Telemetria Fardriver')
plt.subplots_adjust(hspace=0.4, top=0.9, bottom=0.1)

# Desenha as linhas iniciais
line_rpm, = ax1.plot(rpm_data, color='#00ff00', lw=2) # Verde Neon
line_curr, = ax2.plot(current_data, color='#ff9900', lw=2) # Laranja
line_volt, = ax3.plot(voltage_data, color='#00ccff', lw=2) # Ciano

# Formatação Eixo 1: RPM
ax1.set_ylabel('RPM', fontsize=12)
ax1.set_ylim(-100, 6000) # Ajuste este limite máximo para o seu motor
ax1.grid(True, alpha=0.3, ls='--')

# Formatação Eixo 2: Corrente
ax2.set_ylabel('Corrente (A)', fontsize=12)
ax2.set_ylim(-10, 150) # Ajuste para a sua bateria/controladora
ax2.grid(True, alpha=0.3, ls='--')

# Formatação Eixo 3: Tensão
ax3.set_ylabel('Tensão (V)', fontsize=12)
ax3.set_ylim(40, 90) # Ajuste para os limites da sua bateria (Ex: 48V a 84V)
ax3.grid(True, alpha=0.3, ls='--')

# ==========================================
# ANIMAÇÃO: ATUALIZA A TELA 20 VEZES/SEGUNDO
# ==========================================
def update_grafico(frame):
    # Atualiza as curvas
    line_rpm.set_ydata(rpm_data)
    line_curr.set_ydata(current_data)
    line_volt.set_ydata(voltage_data)
    
    # Atualiza os textos do painel
    ax1.set_title(f"MOTOR RPM: {last_values['rpm']} | TEMPERATURA MOTOR: {last_values['temp_motor']}°C", fontsize=14, color='white')
    ax2.set_title(f"CORRENTE: {last_values['curr']:.1f} A | TEMPERATURA MOSFET: {last_values['temp_mosfet']}°C", fontsize=14, color='white')
    ax3.set_title(f"BATERIA: {last_values['volt']:.1f} V", fontsize=14, color='white')
    
    return line_rpm, line_curr, line_volt

# Inicia a Thread que lê a porta USB rodando em paralelo
thread_serial = threading.Thread(target=serial_reader, daemon=True)
thread_serial.start()

# Inicia o Loop da Animação Gráfica
ani = animation.FuncAnimation(fig, update_grafico, interval=50, blit=False)

print("Abrindo Painel Gráfico...")
plt.show()