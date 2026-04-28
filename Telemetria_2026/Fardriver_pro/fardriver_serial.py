import logging
import struct
import threading
import time

import serial

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

# ==============================================================================
# 1. Tabelas de CRC e Endereços (Protocolo Fardriver / Leviatã)
# ==============================================================================
CRC_TABLE_LO = [
    0,
    192,
    193,
    1,
    195,
    3,
    2,
    194,
    198,
    6,
    7,
    199,
    5,
    197,
    196,
    4,
    204,
    12,
    13,
    205,
    15,
    207,
    206,
    14,
    10,
    202,
    203,
    11,
    201,
    9,
    8,
    200,
    216,
    24,
    25,
    217,
    27,
    219,
    218,
    26,
    30,
    222,
    223,
    31,
    221,
    29,
    28,
    220,
    20,
    212,
    213,
    21,
    215,
    23,
    22,
    214,
    210,
    18,
    19,
    211,
    17,
    209,
    208,
    16,
    240,
    48,
    49,
    241,
    51,
    243,
    242,
    50,
    54,
    246,
    247,
    55,
    245,
    53,
    52,
    244,
    60,
    252,
    253,
    61,
    255,
    63,
    62,
    254,
    250,
    58,
    59,
    251,
    57,
    249,
    248,
    56,
    40,
    232,
    233,
    41,
    235,
    43,
    42,
    234,
    238,
    46,
    47,
    239,
    45,
    237,
    236,
    44,
    228,
    36,
    37,
    229,
    39,
    231,
    230,
    38,
    34,
    226,
    227,
    35,
    225,
    33,
    32,
    224,
    160,
    96,
    97,
    161,
    99,
    163,
    162,
    98,
    102,
    166,
    167,
    103,
    165,
    101,
    100,
    164,
    108,
    172,
    173,
    109,
    175,
    111,
    110,
    174,
    170,
    106,
    107,
    171,
    105,
    169,
    168,
    104,
    120,
    184,
    185,
    121,
    187,
    123,
    122,
    186,
    190,
    126,
    127,
    191,
    125,
    189,
    188,
    124,
    180,
    116,
    117,
    181,
    119,
    183,
    182,
    118,
    114,
    178,
    179,
    115,
    177,
    113,
    112,
    176,
    80,
    144,
    145,
    81,
    147,
    83,
    82,
    146,
    150,
    86,
    87,
    151,
    85,
    149,
    148,
    84,
    156,
    92,
    93,
    157,
    95,
    159,
    158,
    94,
    90,
    154,
    155,
    91,
    153,
    89,
    88,
    152,
    136,
    72,
    73,
    137,
    75,
    139,
    138,
    74,
    78,
    142,
    143,
    79,
    141,
    77,
    76,
    140,
    68,
    132,
    133,
    69,
    135,
    71,
    70,
    134,
    130,
    66,
    67,
    131,
    65,
    129,
    128,
    64,
]

CRC_TABLE_HI = [
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
    1,
    192,
    128,
    65,
    1,
    192,
    128,
    65,
    0,
    193,
    129,
    64,
]

FLASH_READ_ADDR = [
    0xE2,
    0xE8,
    0xEE,
    0x00,
    0x06,
    0x0C,
    0x12,
    0xE2,
    0xE8,
    0xEE,
    0x18,
    0x1E,
    0x24,
    0x2A,
    0xE2,
    0xE8,
    0xEE,
    0x30,
    0x5D,
    0x63,
    0x69,
    0xE2,
    0xE8,
    0xEE,
    0x7C,
    0x82,
    0x88,
    0x8E,
    0xE2,
    0xE8,
    0xEE,
    0x94,
    0x9A,
    0xA0,
    0xA6,
    0xE2,
    0xE8,
    0xEE,
    0xAC,
    0xB2,
    0xB8,
    0xBE,
    0xE2,
    0xE8,
    0xEE,
    0xC4,
    0xCA,
    0xD0,
    0xE2,
    0xE8,
    0xEE,
    0xD6,
    0xDC,
    0xF4,
    0xFA,
]

# ==============================================================================
# 2. Mapeamento bit → código de erro (AddrE2, data[2] e data[3])
#    Fonte: fardriver.hpp — struct AddrE2
#
#    data[2] (B4): erros principais
#    data[3] (B5): erros de fase/linha/mosfet
#
#    A lista é ordenada por prioridade — o primeiro bit ativo define o código
#    exibido na UI e no relatório.
# ==============================================================================
_ERROR_BITS = [
    # (byte_index, bit_mask, error_code)
    (2, 0x01, 1),  # motor_hall_error
    (2, 0x02, 2),  # throttle_error
    (2, 0x08, 3),  # phase_current_surge_protect  → alarme anormal
    (2, 0x04, 4),  # current_protect_restart
    (2, 0x10, 5),  # voltage_protect
    (2, 0x40, 7),  # motor_temp_protect
    (2, 0x80, 8),  # controller_temp_protect
    (3, 0x01, 9),  # phase_current_overflow_protect
    (3, 0x02, 10),  # phase_zero_error
    (3, 0x04, 11),  # phase_short_circuit (phase_int16_t_protect)
    (3, 0x08, 12),  # line_current_zero_error
    (3, 0x10, 13),  # mosfet_high_side_error
    (3, 0x20, 14),  # mosfet_low_side_error
    (3, 0x40, 15),  # moe_current_protect
]


def _decode_error(data: bytes) -> int:
    """
    Decodifica os bytes de erro do pacote AddrE2 e retorna o código
    de maior prioridade (menor número), ou 0 se não houver erros.
    """
    for byte_idx, mask, code in _ERROR_BITS:
        if data[byte_idx] & mask:
            return code
    return 0


# ==============================================================================
# Dicionário de descrições de erros Fardriver
# ==============================================================================
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
    15: "PROTEÇÃO PICO DE CORRENTE DE LINHA",
}


# ==============================================================================
# 3. Mapeamento de word-addresses para escrita (protocolo moderno)
#    Fonte: fardriver.hpp — repositório eliasdopontiac/fardriver-controllers
#
#    Os endereços são WORD addresses (não byte). A controladora armazena cada
#    parâmetro em palavras de 16 bits; o endereço 0x19 aponta para a palavra
#    que começa no byte 0x32 da memória flash.
# ==============================================================================
PARAM_ADDR = {
    # Addr18 word 0x19 — MaxLineCurr  (raw = Amperes × 4, uint16 LE)
    "linha_a": 0x19,
    # Addr2A word 0x2D — MaxPhaseCurr (raw = Amperes × 4, uint16 LE)
    "fase_a": 0x2D,
    # Addr30 word 0x30 — StopBackCurr (corrente de início da frenagem regen)
    "regen_stop": 0x30,
    # Addr30 word 0x31 — MaxBackCurr  (pico da frenagem regen ≈ stop × 1.25)
    "regen_max": 0x31,
    # Addr12 word 0x14 — PolePairs @ byte[0], byte[1] = 0x59 (unk14b típico)
    "polos": 0x14,
    # Addr18 word 0x1A — cfg26l (ThrottleResponse bits[3:2], WeakA bits[5:4])
    #                    cfg26h = 0x00 (SpeedPulse/GearConfig — padrão seguro)
    "throttle_weaka": 0x1A,
    # AddrA0 word 0xA0 — SysCmd: byte[0]=0x88, byte[1]=código do comando
    "syscmd": 0xA0,
}

# Códigos de comando de sistema (SysCmd, escritos em PARAM_ADDR["syscmd"])
SYSCMD = {
    "autolearn": 0x02,  # Inicia auto-aprendizado  (AngleLearn → 0xAA)
    "cancel_learn": 0x03,  # Cancela auto-aprendizado (AngleLearn → 0x55)
    "factory_reset": 0x08,  # Restaura parâmetros de fábrica
    "gather_data": 0x06,  # Inicia coleta de 2048 amostras de aceleração
    "stop": 0x07,  # Para operação em andamento
}


def calculate_checksum(data):
    """Calcula o par checksum/not-checksum do protocolo Fardriver."""
    s = sum(data) & 0xFF
    return s, (~s) & 0xFF


def check_crc(header_byte, data_bytes, crc_bytes):
    """Valida o CRC16 de um pacote recebido da controladora."""
    a, b = 0x3C, 0x7F
    full_msg = bytes([0xAA, header_byte]) + data_bytes
    for byte in full_msg:
        crc_i = a ^ byte
        a, b = b ^ CRC_TABLE_HI[crc_i], CRC_TABLE_LO[crc_i]
    return crc_bytes[0] == a and crc_bytes[1] == b


class FardriverSerial:
    """
    Backend de comunicação Serial robusto para a Fardriver ND72450.

    Thread-safety: o dicionário interno `telemetry` é protegido por um
    threading.Lock. Use sempre `ler_dados()` para leitura — ele devolve
    uma cópia snapshot segura.
    """

    # --- Limites operacionais (apenas como referência / validação de UI) ---
    LIMIT_LINE_CURR = 300  # A  — máximo recomendado para corrente de linha
    LIMIT_PHASE_CURR = 800  # A  — máximo absoluto da ND72450
    LIMIT_RPM = 6000  # RPM
    BAUD_RATE = 19200

    def __init__(self):
        self.conectado = False
        self.serial_obj = None
        self.thread = None

        # Coeficiente de torque lido do endereço 0xBE da controladora.
        # Valor padrão 8192 conforme documentação fardriver.hpp.
        # Será atualizado automaticamente quando o pacote 0xBE for recebido.
        self._torque_coeff = 8192

        # Lock que protege _telemetry de acessos simultâneos entre
        # a thread de leitura serial e a thread da UI (QTimer).
        self._lock = threading.Lock()
        self._reset_telemetry()

        # Parâmetros lidos da flash da controladora
        self._params = {}
        self._params_lock = threading.Lock()

        # Watchdog de conexão
        self._last_packet_time = 0.0
        self.on_disconnect_callback = (
            None  # callable() chamado quando watchdog disparar
        )

        # Histórico de erros com timestamp (máx 100 entradas — circular buffer)
        self.error_history = []  # lista de dicts: {"time": str, "code": int, "desc": str}
        self._last_error_code = 0
        self.MAX_ERROR_HISTORY = 100

        # Pacote Keep-Alive que mantém a controladora "acordada"
        cmd, sub, v1, v2 = 0x13, 0x07, 0x01, 0xF1
        p = [cmd, (~cmd) & 0xFF, sub, v1, v2]
        cs, not_cs = calculate_checksum(p)
        self.keep_alive_bytes = bytes([0xAA] + p + [cs, not_cs])

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _reset_telemetry(self):
        """Zera o dicionário de telemetria de forma thread-safe."""
        with self._lock:
            self._telemetry = {
                "rpm": 0,
                "volt": 0.0,
                "curr": 0.0,
                "power": 0.0,
                "torque": 0.0,
                "temp_motor": 0,
                "temp_mosfet": 0,
                "throttle": 0.0,
                "hall_a": False,
                "hall_b": False,
                "hall_c": False,
                "error": 0,
                "batt_soc": 0,
                "forward": False,
                "reverse": False,
                "brake": False,
                "motion": False,
                "phase_offset": 0.0,
            }

    # ------------------------------------------------------------------
    # Conexão
    # ------------------------------------------------------------------

    def conectar(self, porta):
        """Abre a porta serial e inicia a thread de leitura."""
        if not porta or "Nenhuma" in porta:
            return False, "Porta vazia."
        try:
            self.serial_obj = serial.Serial(porta, self.BAUD_RATE, timeout=0.1)

            # Pulso DTR/RTS para resetar adaptadores USB-TTL que precisam disso
            try:
                self.serial_obj.dtr = False
                self.serial_obj.rts = False
                time.sleep(0.1)
                self.serial_obj.dtr = True
                self.serial_obj.rts = True
            except Exception:
                pass  # Nem todos os adaptadores suportam DTR/RTS — ignora

            self.serial_obj.write(self.keep_alive_bytes)
            self.conectado = True
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            logger.info("Conectado em %s @ %d bps", porta, self.BAUD_RATE)
            # Solicita dump completo dos parâmetros da flash
            time.sleep(0.3)  # aguarda estabilização
            self._write_address(
                PARAM_ADDR["syscmd"], bytes([0x88, SYSCMD["gather_data"]]), flags=3
            )
            return True, "OK"
        except serial.SerialException as e:
            self.conectado = False
            logger.error("Falha ao abrir porta %s: %s", porta, e)
            return False, str(e)

    def desconectar(self):
        """Para a thread de leitura e fecha a porta serial."""
        self.conectado = False
        if self.serial_obj:
            try:
                self.serial_obj.close()
            except Exception:
                pass
        if self.thread:
            self.thread.join(timeout=1.0)
        self._reset_telemetry()
        logger.info("Desconectado.")

    # ------------------------------------------------------------------
    # Loop de leitura (thread daemon)
    # ------------------------------------------------------------------

    def _read_loop(self):
        """Thread dedicada à leitura contínua do barramento serial."""
        last_ka = time.time()
        buffer = b""

        while self.conectado:
            try:
                # Keep-Alive a cada 1 segundo
                if time.time() - last_ka > 1.0:
                    self.serial_obj.write(self.keep_alive_bytes)
                    last_ka = time.time()

                if self.serial_obj.in_waiting:
                    buffer += self.serial_obj.read(self.serial_obj.in_waiting)

                # Processa todos os pacotes completos (16 bytes cada) no buffer
                while len(buffer) >= 16:
                    if buffer[0] != 0xAA:
                        # Descarta byte inválido e tenta re-sincronizar
                        buffer = buffer[1:]
                        continue

                    pkt = buffer[:16]
                    if check_crc(pkt[1], pkt[2:14], pkt[14:16]):
                        self._parse_packet(pkt[1], pkt[2:14])
                        buffer = buffer[16:]
                    else:
                        # CRC inválido — descarta o header e tenta re-sincronizar
                        buffer = buffer[1:]

                time.sleep(0.01)

                # Watchdog: sem pacotes por 3 segundos = cabo desconectado
                if (
                    self._last_packet_time > 0
                    and (time.time() - self._last_packet_time) > 3.0
                ):
                    logger.warning("Watchdog: sem pacotes há 3s. Desconectando.")
                    if self.on_disconnect_callback:
                        self.on_disconnect_callback()
                    break

            except serial.SerialException as e:
                # Erro de hardware (cabo desconectado, porta fechada, etc.)
                logger.warning("Erro serial no loop de leitura: %s", e)
                break
            except Exception as e:
                # Qualquer outro erro inesperado é logado mas não silenciado
                logger.exception("Erro inesperado no loop de leitura: %s", e)
                break

        self.conectado = False
        logger.info("Thread de leitura encerrada.")

    # ------------------------------------------------------------------
    # Decodificação de pacotes
    # ------------------------------------------------------------------

    def _parse_packet(self, header, data):
        """Decodifica um pacote válido e atualiza _telemetry com lock."""
        pkt_id = header & 0x3F
        if pkt_id >= len(FLASH_READ_ADDR):
            return
        addr = FLASH_READ_ADDR[pkt_id]

        # Todos os writes em _telemetry são feitos dentro do lock para
        # evitar race conditions com a thread da UI que lê via ler_dados().
        with self._lock:
            t = self._telemetry

            if addr == 0xE8:
                # Tensão e Corrente de linha
                t["volt"] = struct.unpack_from("<h", data, 0)[0] / 10.0
                t["curr"] = struct.unpack_from("<h", data, 4)[0] / 4.0
                t["power"] = t["volt"] * t["curr"]

            elif addr == 0xE2:
                # ── AddrE2 — pacote principal de estado em tempo real ─────────
                #
                # Mapeamento dos 12 bytes de data (índice 0 = byte B2 do pacote):
                #
                #   data[0]    B2  flags: forward, reverse, gear, motion…
                #   data[1]    B3  flags: phaseA_active(b0), phaseB_active(b1),
                #                         phaseC_active(b2), passOK, Bmq_Hall…
                #   data[2]    B4  erros principais (bitmask)
                #   data[3]    B5  erros de fase/linha/mosfet (bitmask)
                #   data[4]    B6  modulation
                #   data[5]    B7  pad
                #   data[6-7]  B8  MeasureSpeed (uint16) → RPM
                #   data[8-9]  B9  unkE6 (int16) → vetor D de corrente
                #   data[10-11] BA unkE7 (int16) → vetor Q de corrente

                # RPM
                t["rpm"] = abs(struct.unpack_from("<h", data, 6)[0])
                if t["rpm"] < 20:
                    t["rpm"] = 0

                # Acelerador (throttle position em milivolts → volts)
                raw_throttle = struct.unpack_from("<H", data, 0)[0]
                if raw_throttle < 6000:
                    t["throttle"] = round(raw_throttle / 1000.0, 2)

                # Sensores Hall — phaseA/B/C_active (bits 0, 1, 2 de data[1])
                # Indicam qual fase do motor está ativamente comutada,
                # refletindo o estado lógico dos sensores Hall naquele instante.
                t["hall_a"] = bool(data[1] & 0x01)
                t["hall_b"] = bool(data[1] & 0x02)
                t["hall_c"] = bool(data[1] & 0x04)

                # Estado de movimento e direção (data[0]) e freio (data[3])
                t["forward"] = bool(data[0] & 0x01)
                t["reverse"] = bool(data[0] & 0x02)
                t["motion"] = bool(data[0] & 0x20)
                t["brake"] = bool(data[3] & 0x80)

                # Código de erro — prioridade: primeiro bit ativo em data[2]/data[3]
                t["error"] = _decode_error(data)

                # Registra novo erro no histórico (evita duplicatas consecutivas)
                new_err = t["error"]
                if new_err != 0 and new_err != self._last_error_code:
                    from datetime import datetime

                    desc = ERROS_FARDRIVER.get(
                        new_err, f"Erro desconhecido ({new_err})"
                    )
                    error_entry = {
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "code": new_err,
                        "desc": desc,
                    }
                    self.error_history.append(error_entry)
                    # Implementa circular buffer (máx 100 erros)
                    if len(self.error_history) > self.MAX_ERROR_HISTORY:
                        self.error_history.pop(0)
                    logger.warning(
                        "[ERRO] %s — %s (código: 0x%02X)", error_entry["time"], desc, new_err
                    )
                self._last_error_code = new_err

                # Torque estimado a partir dos vetores internos de corrente.
                # Fórmula extraída de fardriver.hpp → GetTorque():
                #   torque_raw = ((unkE6² + unkE7²) << 9) / TorqueCoeff
                # Unidade de saída: 0.1 N·m → dividimos por 10 para N·m
                unk_e6 = struct.unpack_from("<h", data, 8)[0]
                unk_e7 = struct.unpack_from("<h", data, 10)[0]
                coeff = self._torque_coeff if self._torque_coeff > 0 else 8192
                torque_raw = ((unk_e6 * unk_e6 + unk_e7 * unk_e7) << 9) // coeff
                t["torque"] = round(torque_raw / 10.0, 1)

            elif addr == 0xF4:
                # Temperatura do Motor
                val = struct.unpack_from("<h", data, 0)[0]
                if -20 < val < 200:
                    t["temp_motor"] = val

                # State of Charge (SOC) em % — data[3]
                soc_val = data[3]
                if 0 <= soc_val <= 100:
                    t["batt_soc"] = int(soc_val)

            elif addr == 0xD6:
                # Temperatura da Controladora (MOSFET)
                val = struct.unpack_from("<h", data, 10)[0]
                if -20 < val < 150:
                    t["temp_mosfet"] = val

            elif addr == 0xBE:
                # TorqueCoeff — coeficiente de calibração do torque.
                # Localização em AddrBE (fardriver.hpp):
                #   bytes[10-11] = TorqueCoeff (uint16)
                # Range documentado: 256–16384, padrão: 8192
                coeff = struct.unpack_from("<H", data, 10)[0]
                if 256 <= coeff <= 16384:
                    self._torque_coeff = coeff
                    logger.debug("[TORQUE] TorqueCoeff atualizado: %d", coeff)

            elif addr == 0x0C:
                # AddrE2 — PID e coeficientes de bateria (fardriver.hpp Addr0C):
                #   data[0-1]  PhaseOffset  (int16, / 10.0 = graus)
                #   data[2-3]  ZeroBattCoeff
                #   data[4-5]  FullBattCoeff
                #   data[6]    StartKI
                #   data[7]    MidKI
                #   data[8]    MaxKI
                #   data[9]    StartKP
                #   data[10]   MidKP
                #   data[11]   MaxKP
                val = struct.unpack_from("<h", data, 0)[0] / 10.0
                if -360.0 <= val <= 360.0:
                    t["phase_offset"] = val

            # === Atualização de _params (parâmetros lidos da flash) ===
            with self._params_lock:
                if addr == 0x12:
                    self._params["LD"] = struct.unpack_from("<h", data, 0)[0]
                    self._params["alarm_delay"] = struct.unpack_from("<H", data, 2)[0]
                    self._params["pole_pairs"] = data[4]
                    self._params["max_speed"] = struct.unpack_from("<H", data, 6)[0]
                    self._params["rated_power"] = struct.unpack_from("<H", data, 8)[0]
                    self._params["rated_voltage"] = (
                        struct.unpack_from("<H", data, 10)[0] / 10.0
                    )

                elif addr == 0x18:
                    self._params["rated_speed"] = struct.unpack_from("<H", data, 0)[0]
                    self._params["max_line_curr"] = (
                        struct.unpack_from("<H", data, 2)[0] / 4.0
                    )
                    cfg26l = data[4]
                    self._params["follow_config"] = cfg26l & 0x03
                    self._params["throttle_response"] = (cfg26l >> 2) & 0x03
                    self._params["weaka"] = (cfg26l >> 4) & 0x03

                elif addr == 0x24:
                    self._params["max_phase_curr"] = (
                        struct.unpack_from("<H", data, 4)[0] / 4.0
                    )
                    self._params["back_speed"] = struct.unpack_from("<H", data, 8)[0]
                    self._params["low_speed"] = struct.unpack_from("<H", data, 10)[0]

                elif addr == 0x0C:
                    self._params["phase_offset"] = (
                        struct.unpack_from("<h", data, 0)[0] / 10.0
                    )
                    self._params["zero_batt_coeff"] = struct.unpack_from("<h", data, 2)[
                        0
                    ]
                    self._params["full_batt_coeff"] = struct.unpack_from("<h", data, 4)[
                        0
                    ]
                    self._params["start_ki"] = data[6]
                    self._params["mid_ki"] = data[7]
                    self._params["max_ki"] = data[8]
                    self._params["start_kp"] = data[9]
                    self._params["mid_kp"] = data[10]
                    self._params["max_kp"] = data[11]

                elif addr == 0x1E:
                    self._params["low_vol_protect"] = (
                        struct.unpack_from("<H", data, 2)[0] / 10.0
                    )

                elif addr == 0x06:
                    cfg11l = data[10]
                    self._params["temp_sensor"] = (cfg11l >> 1) & 0x07
                    self._params["brake_config"] = cfg11l & 0x0F
                    self._params["throttle_low"] = data[6] / 20.0
                    self._params["throttle_high"] = data[7] / 20.0
                    cfg11h = data[11]
                    self._params["direction"] = (cfg11h >> 7) & 0x01

                elif addr == 0x88:
                    self._params["ratio_table_low"] = list(data[:12])

                elif addr == 0x8E:
                    self._params["ratio_table_high"] = list(data[:8])
                    self._params["nratio_table_a"] = [
                        struct.unpack_from("b", data, i)[0] for i in range(8, 12)
                    ]

                elif addr == 0x94:
                    self._params["nratio_table_b"] = [
                        struct.unpack_from("b", data, i)[0] for i in range(0, 12)
                    ]

                elif addr == 0x9A:
                    self._params["nratio_table_c"] = [
                        struct.unpack_from("b", data, i)[0] for i in range(0, 4)
                    ]
                    self._params["AN"] = data[4] & 0x0F
                    self._params["LM"] = data[5] & 0x1F
                    
                    # Consolidar tabelas em estruturas unificadas com 18 pontos
                    # ratio_table: corrente por RPM (18 pontos: min, 500, 1000, ..., max)
                    # nratio_table: regen por RPM (18 pontos, valores signed)
                    ratio_low = self._params.get("ratio_table_low", [0] * 12)
                    ratio_high = self._params.get("ratio_table_high", [0] * 8)
                    nratio_a = self._params.get("nratio_table_a", [0] * 4)
                    nratio_b = self._params.get("nratio_table_b", [0] * 12)
                    nratio_c = self._params.get("nratio_table_c", [0] * 4)
                    
                    rpm_labels = [
                        "min", "500", "1000", "1500", "2000", "2500", "3000",
                        "3500", "4000", "4500", "5000", "5500", "6000", "6500",
                        "7000", "7500", "8000", "max"
                    ]
                    
                    # Montar tabela unificada de corrente (18 pontos)
                    ratio_combined = []
                    ratio_combined.extend(ratio_low[:12])  # min até 5500 RPM
                    ratio_combined.extend(ratio_high[:6])   # 6000 até 7500 RPM (6 valores)
                    ratio_combined.extend(ratio_high[6:8])  # 8000 e max (2 valores)
                    
                    self._params["ratio_table"] = {
                        rpm_labels[i]: ratio_combined[i] for i in range(len(rpm_labels))
                    }
                    
                    # Montar tabela unificada de regen (18 pontos, valores assinados)
                    nratio_combined = []
                    nratio_combined.extend(nratio_a[:4])    # índices 0-3
                    nratio_combined.extend(nratio_b[:12])   # índices 4-15
                    nratio_combined.extend(nratio_c[:2])    # índices 16-17
                    
                    self._params["nratio_table"] = {
                        rpm_labels[i]: nratio_combined[i] for i in range(len(rpm_labels))
                    }

                elif addr == 0x82:
                    self._params["throttle_voltage"] = (
                        struct.unpack_from("<H", data, 0)[0] * 0.01
                    )
                    self._params["motor_temp_protect"] = data[4]
                    self._params["motor_temp_restore"] = data[5]
                    self._params["mos_temp_protect"] = data[6]
                    self._params["mos_temp_restore"] = data[7]
                    self._params["hardware_version"] = (
                        chr(data[9]) if 32 <= data[9] <= 126 else "?"
                    )
                    self._params["software_version_major"] = (
                        chr(data[10]) if 32 <= data[10] <= 126 else "?"
                    )
                    self._params["software_version_minor"] = data[11]

                elif addr == 0x2A:
                    self._params["max_phase_curr2"] = (
                        struct.unpack_from("<H", data, 6)[0] / 4.0
                    )

                elif addr == 0x30:
                    self._params["stop_back_curr"] = struct.unpack_from("<H", data, 0)[
                        0
                    ]
                    self._params["max_back_curr"] = struct.unpack_from("<H", data, 2)[0]

        # Atualiza timestamp do último pacote recebido (usado pelo watchdog)
        self._last_packet_time = time.time()

    # ------------------------------------------------------------------
    # API pública de leitura
    # ------------------------------------------------------------------

    def ler_dados(self):
        """
        Retorna um snapshot thread-safe do dicionário de telemetria.
        Sempre use este método — nunca acesse _telemetry diretamente.
        """
        with self._lock:
            return self._telemetry.copy()

    def get_params(self) -> dict:
        """
        Retorna uma cópia thread-safe do dicionário de parâmetros da flash.
        Atualizado automaticamente quando os pacotes de configuração são recebidos.
        """
        with self._params_lock:
            return self._params.copy()

    def get_error_history(self) -> list:
        """
        Retorna uma cópia da lista de histórico de erros (máx 100 entradas).
        Cada entrada contém: {"time": "HH:MM:SS.mmm", "code": int, "desc": str}
        """
        return self.error_history.copy()

    def clear_error_history(self):
        """Limpa o histórico de erros (p.ex., após exportar ou em novo teste)."""
        self.error_history.clear()
        self._last_error_code = 0

    # ------------------------------------------------------------------
    # API pública de escrita / configuração
    # ------------------------------------------------------------------

    def _enviar_pacote(self, cmd, subcmd, val1, val2):
        """
        Protocolo LEGADO (checksum simples) — mantido apenas para o Keep-Alive.
        Para escrita de parâmetros use _write_address().
        """
        if not self.conectado or not self.serial_obj:
            return False
        try:
            p = [cmd, (~cmd) & 0xFF, subcmd, val1, val2]
            cs, not_cs = calculate_checksum(p)
            pacote = bytes([0xAA] + p + [cs, not_cs])
            self.serial_obj.write(pacote)
            return True
        except serial.SerialException as e:
            logger.error("Falha ao enviar pacote legado: %s", e)
            return False

    # ------------------------------------------------------------------
    # Protocolo moderno — Write Address Direct
    # ------------------------------------------------------------------

    def _compute_crc16(self, payload: bytes):
        """
        CRC16 Fardriver — idêntico ao usado nos pacotes de leitura.
        Aplica-se sobre todos os bytes do pacote ANTES dos 2 bytes de CRC.
        """
        a, b = 0x3C, 0x7F
        for byte in payload:
            i = a ^ byte
            a = b ^ CRC_TABLE_HI[i]
            b = CRC_TABLE_LO[i]
        return a, b

    def _write_address(self, addr: int, data: bytes, flags: int = 1) -> bool:
        """
        Envia um pacote de escrita usando o protocolo moderno Write Address Direct.

        Estrutura do pacote (8 bytes para payload de 2 bytes):
            0xAA | byte1 | addr | addr_confirm | data[0..N] | crc_a | crc_b

        byte1 = (compute_length & 0x3F) | (flags << 6)
        compute_length = total_length - 2  (exclui os 2 bytes de CRC)

        flags:
            1 — escrita normal de parâmetro  (ex.: corrente, polos)
            3 — SysCmd / comando de sistema  (ex.: autolearn, factory reset)

        O CRC16 é calculado sobre todos os bytes anteriores ao CRC
        usando o mesmo algoritmo dos pacotes de leitura (ComputeCRC).
        """
        if not self.conectado or not self.serial_obj:
            return False

        # total = 0xAA(1) + byte1(1) + addr(1) + addr_confirm(1) + data(N) + crc(2)
        total_len = 4 + len(data) + 2
        compute_length = total_len - 2
        byte1 = (compute_length & 0x3F) | ((flags & 0x03) << 6)

        payload = bytes([0xAA, byte1, addr, addr]) + data
        crc_a, crc_b = self._compute_crc16(payload)
        pacote = payload + bytes([crc_a, crc_b])

        try:
            self.serial_obj.write(pacote)
            logger.debug(
                "[WR] addr=0x%02X flags=%d data=%s → pkt=%s",
                addr,
                flags,
                data.hex(),
                pacote.hex(),
            )
            return True
        except serial.SerialException as e:
            logger.error("Falha ao escrever addr=0x%02X: %s", addr, e)
            return False

    # ------------------------------------------------------------------
    # API pública de escrita / configuração
    # ------------------------------------------------------------------

    def enviar_configuracoes(self, config_dict: dict) -> bool:
        """
        Envia parâmetros para a controladora usando Write Address Direct (flags=1).

        Word-addresses e escalas extraídos do fardriver.hpp
        (repositório eliasdopontiac/fardriver-controllers):

            linha_a   → word 0x19  MaxLineCurr    raw = A × 4       (uint16 LE)
            fase_a    → word 0x2D  MaxPhaseCurr   raw = A × 4       (uint16 LE)
            regen_a   → word 0x30  StopBackCurr   raw = A direto    (uint16 LE)
                      → word 0x31  MaxBackCurr    raw = A × 1.25   (uint16 LE)
            polos     → word 0x14  PolePairs      byte[0]=polos, byte[1]=0x59
            throttle  → word 0x1A  cfg26l bits[3:2] (0=Line,1=Sport,2=ECO)
            weaka     → word 0x1A  cfg26l bits[5:4] (0-3) — mesmo word que throttle

        ATENÇÃO: Um reset da controladora é necessário para que os novos
        valores de polos, tensão nominal e direção entrem em vigor.
        """
        if not self.conectado:
            logger.warning("enviar_configuracoes: não conectado.")
            return False

        enviados = 0

        # ── Corrente de linha (MaxLineCurr) ───────────────────────────────
        if "linha_a" in config_dict:
            raw = int(round(config_dict["linha_a"] * 4)) & 0xFFFF
            if self._write_address(PARAM_ADDR["linha_a"], struct.pack("<H", raw)):
                enviados += 1
                logger.info(
                    "[WRITE] MaxLineCurr = %d A  (raw=%d, word=0x%02X)",
                    config_dict["linha_a"],
                    raw,
                    PARAM_ADDR["linha_a"],
                )

        # ── Corrente de fase (MaxPhaseCurr) ───────────────────────────────
        if "fase_a" in config_dict:
            raw = int(round(config_dict["fase_a"] * 4)) & 0xFFFF
            if self._write_address(PARAM_ADDR["fase_a"], struct.pack("<H", raw)):
                enviados += 1
                logger.info(
                    "[WRITE] MaxPhaseCurr = %d A  (raw=%d, word=0x%02X)",
                    config_dict["fase_a"],
                    raw,
                    PARAM_ADDR["fase_a"],
                )

        # ── Corrente de frenagem regen (StopBackCurr + MaxBackCurr) ──────
        # StopBackCurr: corrente de início da frenagem (valor direto em A)
        # MaxBackCurr : pico da frenagem ≈ StopBack × 1.25 (limite de segurança)
        if "regen_a" in config_dict:
            stop_raw = int(config_dict["regen_a"]) & 0xFFFF
            max_raw = int(round(config_dict["regen_a"] * 1.25)) & 0xFFFF
            if self._write_address(
                PARAM_ADDR["regen_stop"], struct.pack("<H", stop_raw)
            ):
                enviados += 1
                logger.info(
                    "[WRITE] StopBackCurr = %d A  (raw=%d)",
                    config_dict["regen_a"],
                    stop_raw,
                )
            if self._write_address(PARAM_ADDR["regen_max"], struct.pack("<H", max_raw)):
                enviados += 1
                logger.info("[WRITE] MaxBackCurr raw=%d", max_raw)

        # ── Pares de polos (PolePairs) ────────────────────────────────────
        # Byte[0] = número de pares de polos (1–40)
        # Byte[1] = unk14b — mantido em 0x59 (valor típico observado no .hpp)
        if "polos" in config_dict:
            pole = int(config_dict["polos"]) & 0xFF
            if self._write_address(PARAM_ADDR["polos"], bytes([pole, 0x59])):
                enviados += 1
                logger.info(
                    "[WRITE] PolePairs = %d  (word=0x%02X)",
                    config_dict["polos"],
                    PARAM_ADDR["polos"],
                )

        # ── Throttle Response + WeakA (word 0x1A, byte cfg26l) ───────────
        # Estrutura do byte cfg26l (low byte de Addr18 word 0x1A):
        #   bits [1:0] = FollowConfig  → 0  (Follow habilitado — padrão seguro)
        #   bits [3:2] = ThrottleResponse  (0=Line, 1=Sport, 2=ECO)
        #   bits [5:4] = WeakA             (0=desligado … 3=máximo)
        #   bits [7:6] = RXD           → 0  (AF mode — padrão seguro)
        # cfg26h (byte[1]) → 0x00  (SpeedPulse/GearConfig — sem alteração)
        if "throttle" in config_dict or "weaka" in config_dict:
            t_bits = int(config_dict.get("throttle", 0)) & 0x03
            w_bits = int(config_dict.get("weaka", 0)) & 0x03
            cfg26l = (w_bits << 4) | (t_bits << 2)  # FollowConfig=0, RXD=0
            if self._write_address(PARAM_ADDR["throttle_weaka"], bytes([cfg26l, 0x00])):
                enviados += 1
                logger.info(
                    "[WRITE] ThrottleResponse=%d WeakA=%d  (cfg26l=0x%02X, word=0x%02X)",
                    t_bits,
                    w_bits,
                    cfg26l,
                    PARAM_ADDR["throttle_weaka"],
                )

        if enviados == 0:
            logger.warning("enviar_configuracoes: nenhum parâmetro conhecido no dict.")
            return False

        logger.info("enviar_configuracoes: %d escrita(s) enviada(s).", enviados)
        return True

    def iniciar_autolearn(self) -> bool:
        """
        Dispara o Auto-Aprendizado de posição do rotor (SysCmd 0x02).

        Protocolo moderno: escreve [0x88, 0x02] no word address 0xA0 com flags=3.
        Confirmação: a controladora emite 2 bipes curtos + 1 longo.
        Para cancelar, use cancelar_autolearn().
        """
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Iniciar Auto-Learn (0x02)")
        return self._write_address(
            PARAM_ADDR["syscmd"],
            bytes([0x88, SYSCMD["autolearn"]]),
            flags=3,
        )

    def cancelar_autolearn(self) -> bool:
        """Cancela o Auto-Aprendizado em curso (SysCmd 0x03)."""
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Cancelar Auto-Learn (0x03)")
        return self._write_address(
            PARAM_ADDR["syscmd"],
            bytes([0x88, SYSCMD["cancel_learn"]]),
            flags=3,
        )

    def restaurar_fabrica(self) -> bool:
        """
        Restaura os parâmetros de fábrica (SysCmd 0x08).

        Protocolo moderno: escreve [0x88, 0x08] no word address 0xA0 com flags=3.
        Pacote completo verificado: AA C6 A0 A0 88 08 C5 09
        """
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Restaurar Fábrica (0x08)")
        return self._write_address(
            PARAM_ADDR["syscmd"],
            bytes([0x88, SYSCMD["factory_reset"]]),
            flags=3,
        )

    def iniciar_coleta_dados(self) -> bool:
        """
        Inicia a coleta de 2048 amostras do ciclo de aceleração (SysCmd 0x06).
        Os dados ficam armazenados na flash da controladora e podem ser
        lidos pela função de 'Gather Data' do software oficial Fardriver.
        """
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Iniciar Coleta de Dados (0x06)")
        return self._write_address(
            PARAM_ADDR["syscmd"],
            bytes([0x88, SYSCMD["gather_data"]]),
            flags=3,
        )
