import serial
import time
import threading
import struct

# ==============================================================================
# 1. Tabelas de CRC e Endereços (Protocolo Fardriver / Leviatã)
# ==============================================================================
CRC_TABLE_LO = [
    0, 192, 193, 1, 195, 3, 2, 194, 198, 6, 7, 199, 5, 197, 196, 4, 204, 12, 13, 205, 15, 207, 206, 14, 10, 202, 203, 11, 201, 9, 8, 200, 216, 24, 25, 217, 27, 219, 218, 26, 30, 222, 223, 31, 221, 29, 28, 220, 20, 212, 213, 21, 215, 23, 22, 214, 210, 18, 19, 211, 17, 209, 208, 16, 240, 48, 49, 241, 51, 243, 242, 50, 54, 246, 247, 55, 245, 53, 52, 244, 60, 252, 253, 61, 255, 63, 62, 254, 250, 58, 59, 251, 57, 249, 248, 56, 40, 232, 233, 41, 235, 43, 42, 234, 238, 46, 47, 239, 45, 237, 236, 44, 228, 36, 37, 229, 39, 231, 230, 38, 34, 226, 227, 35, 225, 33, 32, 224, 160, 96, 97, 161, 99, 163, 162, 98, 102, 166, 167, 103, 165, 101, 100, 164, 108, 172, 173, 109, 175, 111, 110, 174, 170, 106, 107, 171, 105, 169, 168, 104, 120, 184, 185, 121, 187, 123, 122, 186, 190, 126, 127, 191, 125, 189, 188, 124, 180, 116, 117, 181, 119, 183, 182, 118, 114, 178, 179, 115, 177, 113, 112, 176, 80, 144, 145, 81, 147, 83, 82, 146, 150, 86, 87, 151, 85, 149, 148, 84, 156, 92, 93, 157, 95, 159, 158, 94, 90, 154, 155, 91, 153, 89, 88, 152, 136, 72, 73, 137, 75, 139, 138, 74, 78, 142, 143, 79, 141, 77, 76, 140, 68, 132, 133, 69, 135, 71, 70, 134, 130, 66, 67, 131, 65, 129, 128, 64
]

CRC_TABLE_HI = [
    0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64, 0, 193, 129, 64, 1, 192, 128, 65, 0, 193, 129, 64, 1, 192, 128, 65, 1, 192, 128, 65, 0, 193, 129, 64
]

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

def calculate_checksum(data):
    s = sum(data) & 0xFF
    return s, (~s) & 0xFF

def check_crc(header_byte, data_bytes, crc_bytes):
    a, b = 0x3C, 0x7F
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    for byte in full_msg:
        crc_i = a ^ byte
        a, b = b ^ CRC_TABLE_HI[crc_i], CRC_TABLE_LO[crc_i]
    return crc_bytes[0] == a and crc_bytes[1] == b

class FardriverSerial:
    """
    Backend de comunicação Serial robusto para a Fardriver ND72450.
    """
    LIMIT_LINE_CURR = 300
    LIMIT_PHASE_CURR = 800
    LIMIT_RPM = 6000
    BAUD_RATE = 19200

    def __init__(self):
        self.LIMIT_LINE_CURR = 300
        self.LIMIT_PHASE_CURR = 800
        self.LIMIT_RPM = 6000
        
        self.conectado = False
        self.serial_obj = None
        self.thread = None
        self._reset_telemetry()
        
        # Pacote Keep-Alive que acorda a placa
        cmd, sub, v1, v2 = 0x13, 0x07, 0x01, 0xF1
        p = [cmd, (~cmd) & 0xFF, sub, v1, v2]
        cs, not_cs = calculate_checksum(p)
        self.keep_alive_bytes = bytes([0xAA] + p + [cs, not_cs])

    def _reset_telemetry(self):
        self.telemetry = {
            "rpm": 0, "volt": 0.0, "curr": 0.0, "power": 0.0, "torque": 0.0,
            "temp_motor": 0, "temp_mosfet": 0, "throttle": 0.0,
            "hall_a": False, "hall_b": False, "hall_c": False, "error": 0
        }

    def conectar(self, porta):
        if not porta or "Nenhuma" in porta: return False, "Porta vazia."
        try:
            self.serial_obj = serial.Serial(porta, self.BAUD_RATE, timeout=0.1)
            
            try:
                self.serial_obj.dtr = False
                self.serial_obj.rts = False
                time.sleep(0.1)
                self.serial_obj.dtr = True
                self.serial_obj.rts = True
            except: pass

            self.serial_obj.write(self.keep_alive_bytes)
            self.conectado = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            return True, "OK"
        except Exception as e:
            self.conectado = False
            return False, str(e)

    def desconectar(self):
        self.conectado = False
        if self.serial_obj:
            try: self.serial_obj.close()
            except: pass
        if self.thread: self.thread.join(timeout=0.5)
        self._reset_telemetry()

    def _read_loop(self):
        last_ka = time.time()
        buffer = b''
        while self.conectado:
            try:
                if time.time() - last_ka > 1.0:
                    self.serial_obj.write(self.keep_alive_bytes)
                    last_ka = time.time()
                
                if self.serial_obj.in_waiting:
                    buffer += self.serial_obj.read(self.serial_obj.in_waiting)
                
                while len(buffer) >= 16:
                    if buffer[0] != 0xAA:
                        buffer = buffer[1:]; continue
                    pkt = buffer[:16]
                    if check_crc(pkt[1], pkt[2:14], pkt[14:16]):
                        self._parse_packet(pkt[1], pkt[2:14])
                        buffer = buffer[16:]
                    else:
                        buffer = buffer[1:]
                time.sleep(0.01)
            except: break
        self.conectado = False

    def _parse_packet(self, header, data):
        pkt_id = header & 0x3F
        if pkt_id >= len(FLASH_READ_ADDR): return
        addr = FLASH_READ_ADDR[pkt_id]
        t = self.telemetry
        
        if addr == 0xE8:
            # Tensão e Corrente
            t["volt"] = struct.unpack_from('<h', data, 0)[0] / 10.0
            t["curr"] = struct.unpack_from('<h', data, 4)[0] / 4.0
            t["power"] = t["volt"] * t["curr"]
            
        elif addr == 0xE2:
            # RPM 
            t["rpm"] = abs(struct.unpack_from('<h', data, 6)[0])
            if t["rpm"] < 20: t["rpm"] = 0
            
            # Acelerador na ND72450 (Bytes 0 e 1 em milivolts)
            raw_throttle = struct.unpack_from('<H', data, 0)[0]
            if raw_throttle < 6000:
                t["throttle"] = round(raw_throttle / 1000.0, 2)
                
        elif addr == 0xF4:
            # Temperatura do Motor (Local Padrão Oficial)
            val = struct.unpack_from('<h', data, 0)[0]
            if -20 < val < 200:
                t["temp_motor"] = val
                
        elif addr == 0xD6:
            # Temperatura da Controladora (Local Padrão Oficial)
            val = struct.unpack_from('<h', data, 10)[0]
            if -20 < val < 150:
                t["temp_mosfet"] = val
                
        elif addr == 0x0C:
            # Erros e Sensores Hall
            t["error"] = data[0]
            t["hall_a"] = bool(data[2] & 1)
            t["hall_b"] = bool(data[2] & 2)
            t["hall_c"] = bool(data[2] & 4)

    def ler_dados(self):
        return self.telemetry

    def _enviar_pacote(self, cmd, subcmd, val1, val2):
        """Função interna para montar e disparar pacotes de configuração"""
        if not self.conectado or not self.serial_obj: return False
        try:
            p = [cmd, (~cmd) & 0xFF, subcmd, val1, val2]
            cs, not_cs = calculate_checksum(p)
            pacote = bytes([0xAA] + p + [cs, not_cs])
            self.serial_obj.write(pacote)
            return True
        except Exception as e:
            print(f"[ERRO SERIAL] Falha ao enviar: {e}")
            return False

    def enviar_configuracoes(self, config_dict):
        if not self.conectado: return False
        print(f"[COMANDO] Gravar Parâmetros: {config_dict}")
        # Comando de Escrita (0x12) - Exemplo genérico
        # A lógica exata bit-a-bit de gravação vai depender do mapeamento da placa
        self._enviar_pacote(0x12, 0x07, 0x00, 0x00) 
        return True

    def iniciar_autolearn(self):
        if not self.conectado: return False
        print("[COMANDO] Iniciar Auto-Learn...")
        # Dispara o comando de Auto-Learn (Write 0x12, Endereço comum do AutoLearn = 1)
        return self._enviar_pacote(0x12, 0x07, 0x16, 0x01)

    def restaurar_fabrica(self):
        if not self.conectado: return False
        print("[COMANDO] Restaurar Fábrica!")
        # Dispara o comando de Reset de Fábrica
        return self._enviar_pacote(0x12, 0x07, 0x15, 0x01)