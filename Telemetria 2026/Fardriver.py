import serial
import time
import struct
import sys

# Configurações da Porta Serial (AJUSTE AQUI SEU COM/TTY)
SERIAL_PORT = 'COM5'  # No Windows ex: 'COM3', no Linux ex: '/dev/ttyUSB0'
BAUD_RATE = 19200

# ==============================================================================
# 1. Tabelas de CRC (Extraídas de fardriver_message.hpp)
# ==============================================================================
CRC_TABLE_LO = [
    0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64
]

CRC_TABLE_HI = [
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64
]

# Tabela de mapeamento de ID do pacote para endereço de memória da Fardriver
# Índice do array = Header ID, Valor = Endereço base (ex: 0xE8)
FLASH_READ_ADDR = [
    0xE2, 0xE8, 0xEE, 0x00, 0x06, 0x0C, 0x12, 
    0xE2, 0xE8, 0xEE, 0x18, 0x1E, 0x24, 0x2A, 
    0xE2, 0xE8, 0xEE, 0x30, 0x5D, 0x63, 0x69, 
    0xE2, 0xE8, 0xEE, 0x7C, 0x82, 0x88, 0x8E, 
    0xE2, 0xE8, 0xEE, 0x94, 0x9A, 0xA0, 0xA6, 
    0xE2, 0xE8, 0xEE, 0xAC, 0xB2, 0xB8, 0xBE, 
    0xE2, 0xE8, 0xEE, 0xC4, 0xCA, 0xD0,
    0xE2, 0xE8, 0xEE, 0xD6, 0xDC, 0xF4, 0xFA
]

# ==============================================================================
# 2. Funções Auxiliares
# ==============================================================================

def calculate_checksum(data):
    """Calcula o checksum simples usado no pacote 'Keep Alive'."""
    s = sum(data) & 0xFF
    return s, (~s) & 0xFF

def check_crc(header_byte, data_bytes, crc_bytes):
    """Verifica o CRC16 usando as tabelas copiadas do C++."""
    a = 0x3C
    b = 0x7F
    
    # O CRC original do C++ INCLUI o byte 0xAA no cálculo!
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    
    for byte in full_msg:
        crc_i = a ^ byte
        a = b ^ CRC_TABLE_HI[crc_i]
        b = CRC_TABLE_LO[crc_i]
        
    return crc_bytes[0] == a and crc_bytes[1] == b

# ==============================================================================
# 3. Lógica Principal
# ==============================================================================

class FardriverMonitor:
    def __init__(self, port, baud):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        self.data_store = {
            "rpm": 0,
            "voltage": 0.0,
            "current": 0.0,
            "temp_motor": 0,
            "temp_mosfet": 0,
            "throttle": 0
        }
        self.last_print_time = 0  # <--- Adicione esta linha
    
    def send_keep_alive(self):
        """Envia o comando de inicialização (Open)."""
        # Comando: 0x13, 0x07, 0x01, 0xF1 (Baseado no fardriver_controller.hpp)
        # Formato: AA CMD ~CMD SUB V1 V2 CS ~CS
        cmd = 0x13
        sub = 0x07
        v1 = 0x01
        v2 = 0xF1
        
        packet = [0xAA, cmd, (~cmd) & 0xFF, sub, v1, v2]
        cs, not_cs = calculate_checksum(packet[1:]) # Checksum soma do índice 1 ao 5
        packet.append(cs)
        packet.append(not_cs)
        
        self.ser.write(bytes(packet))
        # print(f"Enviado Keep Alive: {[hex(x) for x in packet]}")

    def parse_packet(self, header, data):
        """Extrai dados baseados no ID do pacote."""
        pkt_id = header & 0x3F # Primeiros 6 bits são o ID
        
        if pkt_id >= len(FLASH_READ_ADDR):
            return

        addr_type = FLASH_READ_ADDR[pkt_id]

        # Mapeamento baseado em fardriver.hpp
        
        # Pacote 0xE8: Voltagem e Corrente
        if addr_type == 0xE8:
            # deci_volts (bytes 0-1), lineCurrent (bytes 4-5)
            # Struct format: <h (short little endian)
            raw_volts = struct.unpack_from('<h', data, 0)[0]
            raw_curr = struct.unpack_from('<h', data, 4)[0]
            
            self.data_store["voltage"] = raw_volts / 10.0
            self.data_store["current"] = raw_curr / 4.0
            
        # Pacote 0xE2: RPM (MeasureSpeed)
      
        elif addr_type == 0xE2:
            # Lê o valor podendo ser negativo
            raw_rpm = struct.unpack_from('<h', data, 6)[0]
            
            # Pega o valor absoluto (transforma -400 em 400, por exemplo)
            rpm_real = abs(raw_rpm)
            
            # Filtro para ruído com o motor parado (ignora flutuações menores que 20)
            if rpm_real < 20:
                rpm_real = 0
                
            self.data_store["rpm"] = rpm_real

        # Pacote 0xF4: Temperatura do Motor
        elif addr_type == 0xF4:
             # motor_temp está nos bytes 0-1
             raw_m_temp = struct.unpack_from('<h', data, 0)[0]
             self.data_store["temp_motor"] = raw_m_temp 

        # Pacote 0xD6: Temperatura Mosfet
        elif addr_type == 0xD6:
             # MosTemp está nos bytes 10-11 (offset de struct AddrD6)
             # Espera, AddrD6 tem 2 bytes (int16) no final. 
             # No C++: offsetof(FardriverData, addrD6) == 0xD6 << 1
             # Vamos olhar o struct AddrD6 no arquivo .hpp:
             # Tem vários bitfields no começo. MosTemp é o último int16_t.
             # O tamanho total é 12 bytes. MosTemp são os últimos 2 bytes (10 e 11).
             raw_mos_temp = struct.unpack_from('<h', data, 10)[0]
             self.data_store["temp_mosfet"] = raw_mos_temp

    def run(self):
        print(f"Abrindo porta {self.ser.port}...")
        time.sleep(1)
        
        self.send_keep_alive()
        last_keep_alive = time.time()
        
        buffer = b''
        
        try:
            while True:
                if time.time() - last_keep_alive > 1.0:
                    self.send_keep_alive()
                    last_keep_alive = time.time()

                if self.ser.in_waiting:
                    new_data = self.ser.read(self.ser.in_waiting)
                    buffer += new_data
                    # === LINHA DE DEBUG ===
                    # Imprime na tela tudo o que chega em formato Hexadecimal
                    
                
                while len(buffer) >= 16:
                    if buffer[0] != 0xAA:
                        buffer = buffer[1:]
                        continue
                    
                    packet = buffer[:16]
                    header = packet[1]
                    data = packet[2:14]
                    crc = packet[14:16]
                    
                    if check_crc(header, data, crc):
                        self.parse_packet(header, data)
                        self.print_dashboard()
                        buffer = buffer[16:]
                    else:
                        # === LINHA DE DEBUG ===
                        
                        buffer = buffer[1:]

                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\nEncerrando...")
            self.ser.close()

    def print_dashboard(self):
        agora = time.time()
        
        # Só imprime se já passou 0.25 segundos desde a última impressão
        if agora - self.last_print_time > 0.25:
            msg = (
                f"RPM: {self.data_store['rpm']:<5} | "
                f"Bateria: {self.data_store['voltage']:>5.1f} V | "
                f"Corrente: {self.data_store['current']:>5.1f} A | "
                f"Motor: {self.data_store['temp_motor']:>3} C | "
                f"Mosfet: {self.data_store['temp_mosfet']:>3} C"
            )
            
            # O \r faz o cursor voltar para o começo da linha em vez de pular linha
            # Os espaços no final apagam o "lixo" de textos mais longos anteriores
            sys.stdout.write("\r" + msg + " " * 10)
            sys.stdout.flush()
            
            self.last_print_time = agora

if __name__ == "__main__":
    monitor = FardriverMonitor(SERIAL_PORT, BAUD_RATE)
    monitor.run()