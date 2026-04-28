import logging
import struct
import threading
import time
from datetime import datetime

import serial

logger = logging.getLogger(__name__)

# ==============================================================================
# Tabelas CRC16 (Fardriver protocol)
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

# Flash read address lookup — maps packet id (0x00..0x36) to memory address
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
# Error bit → error code mapping  (source: AddrE2 data[2] and data[3])
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

# (byte_index_in_data, bitmask, error_code) — ordered by priority
_ERROR_BITS = [
    (2, 0x01, 1),  # motor_hall_error
    (2, 0x02, 2),  # throttle_error
    (2, 0x08, 3),  # phase_current_surge_protect
    (2, 0x04, 4),  # current_protect_restart
    (2, 0x10, 5),  # voltage_protect
    (2, 0x40, 7),  # motor_temp_protect
    (2, 0x80, 8),  # controller_temp_protect
    (3, 0x01, 9),  # phase_current_overflow
    (3, 0x02, 10),  # phase_zero_error
    (3, 0x04, 11),  # phase_short_circuit
    (3, 0x08, 12),  # line_current_zero_error
    (3, 0x10, 13),  # mosfet_high_side_error
    (3, 0x20, 14),  # mosfet_low_side_error
    (3, 0x40, 15),  # moe_current_protect
]


def _decode_error(data: bytes) -> int:
    """Return the highest-priority active error code, or 0 if none."""
    for byte_idx, mask, code in _ERROR_BITS:
        if len(data) > byte_idx and data[byte_idx] & mask:
            return code
    return 0


# ==============================================================================
# Write-address map  (word addresses, source: fardriver.hpp)
# ==============================================================================
PARAM_ADDR = {
    "linha_a": 0x19,  # Addr18 — MaxLineCurr    (raw = A×4, uint16 LE)
    "fase_a": 0x2D,  # Addr2A — MaxPhaseCurr   (raw = A×4, uint16 LE)
    "regen_stop": 0x30,  # Addr30 — StopBackCurr
    "regen_max": 0x31,  # Addr30 — MaxBackCurr
    "polos": 0x14,  # Addr12 — PolePairs      (byte[0], byte[1]=0x59)
    "throttle_weaka": 0x1A,  # Addr18 — cfg26l
    "syscmd": 0xA0,  # AddrA0 — SysCmd         (byte[0]=0x88, byte[1]=cmd)
}

SYSCMD = {
    "autolearn": 0x02,
    "cancel_learn": 0x03,
    "factory_reset": 0x08,
    "gather_data": 0x06,
    "stop": 0x07,
}


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


# ==============================================================================
# FardriverSerial
# ==============================================================================
class FardriverSerial:
    """
    Thread-safe serial backend for the Fardriver ND72450 controller.

    All reads of _telemetry must go through ler_dados() which returns a
    copy under _lock.  All writes to _telemetry happen inside _parse_packet
    which also holds _lock.
    """

    LIMIT_LINE_CURR = 300  # A
    LIMIT_PHASE_CURR = 800  # A
    LIMIT_RPM = 6000  # RPM
    BAUD_RATE = 19200

    def __init__(self):
        self.conectado = False
        self.serial_obj = None
        self.thread = None

        # --- Locks ----------------------------------------------------------
        self._lock = threading.Lock()
        self._params_lock = threading.Lock()

        # --- Telemetry (real-time) ------------------------------------------
        self._reset_telemetry()

        # --- Parameters (flash snapshot) ------------------------------------
        self._params: dict = {}

        # --- Error history --------------------------------------------------
        self.error_history: list[dict] = []  # {"time", "code", "desc"}
        self._last_error_code = 0

        # --- Watchdog -------------------------------------------------------
        self._last_packet_time = 0.0
        self.on_disconnect_callback = None  # callable — called from reader thread

        # --- Torque coefficient (default per fardriver.hpp) -----------------
        self._torque_coeff = 8192

        # --- Keep-alive packet (legacy protocol) ----------------------------
        cmd, sub, v1, v2 = 0x13, 0x07, 0x01, 0xF1
        p = [cmd, (~cmd) & 0xFF, sub, v1, v2]
        cs, not_cs = calculate_checksum(p)
        self.keep_alive_bytes = bytes([0xAA] + p + [cs, not_cs])

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_telemetry(self):
        with self._lock:
            self._telemetry = {
                # Power
                "rpm": 0,
                "volt": 0.0,
                "curr": 0.0,
                "power": 0.0,
                "torque": 0.0,
                # Temperatures
                "temp_motor": 0,
                "temp_mosfet": 0,
                # Throttle
                "throttle": 0.0,
                # Hall sensors
                "hall_a": False,
                "hall_b": False,
                "hall_c": False,
                # Error
                "error": 0,
                # Battery SOC
                "batt_soc": 0,
                # Motion status
                "forward": False,
                "reverse": False,
                "brake": False,
                "motion": False,
                # Diagnostics
                "phase_offset": 0.0,
            }

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def conectar(self, porta: str):
        if not porta or "Nenhuma" in porta:
            return False, "Porta vazia."
        try:
            self.serial_obj = serial.Serial(porta, self.BAUD_RATE, timeout=0.1)
            try:
                self.serial_obj.dtr = False
                self.serial_obj.rts = False
                time.sleep(0.1)
                self.serial_obj.dtr = True
                self.serial_obj.rts = True
            except Exception:
                pass

            self.serial_obj.write(self.keep_alive_bytes)
            self.conectado = True
            self._last_packet_time = time.time()
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()
            logger.info("Conectado em %s @ %d bps", porta, self.BAUD_RATE)

            # Request full flash dump so params tab gets populated
            time.sleep(0.3)
            self._write_address(
                PARAM_ADDR["syscmd"],
                bytes([0x88, SYSCMD["gather_data"]]),
                flags=3,
            )
            return True, "OK"
        except serial.SerialException as e:
            self.conectado = False
            logger.error("Falha ao abrir %s: %s", porta, e)
            return False, str(e)

    def desconectar(self):
        self.conectado = False
        if self.serial_obj:
            try:
                self.serial_obj.close()
            except Exception:
                pass
        if self.thread:
            self.thread.join(timeout=1.0)
        self._reset_telemetry()
        with self._params_lock:
            self._params = {}
        logger.info("Desconectado.")

    # ------------------------------------------------------------------
    # Reader thread
    # ------------------------------------------------------------------

    def _read_loop(self):
        last_ka = time.time()
        buffer = b""

        while self.conectado:
            try:
                # Keep-alive every 1 s
                if time.time() - last_ka > 1.0:
                    self.serial_obj.write(self.keep_alive_bytes)
                    last_ka = time.time()

                if self.serial_obj.in_waiting:
                    buffer += self.serial_obj.read(self.serial_obj.in_waiting)

                while len(buffer) >= 16:
                    if buffer[0] != 0xAA:
                        buffer = buffer[1:]
                        continue
                    pkt = buffer[:16]
                    if check_crc(pkt[1], pkt[2:14], pkt[14:16]):
                        self._parse_packet(pkt[1], pkt[2:14])
                        self._last_packet_time = time.time()
                        buffer = buffer[16:]
                    else:
                        buffer = buffer[1:]

                time.sleep(0.01)

                # Watchdog: no packets for 3 s → assume cable disconnected
                if (
                    self._last_packet_time > 0
                    and time.time() - self._last_packet_time > 3.0
                ):
                    logger.warning("Watchdog: sem pacotes há 3 s — desconectando.")
                    if self.on_disconnect_callback:
                        self.on_disconnect_callback()
                    break

            except serial.SerialException as e:
                logger.warning("Erro serial no loop: %s", e)
                break
            except Exception as e:
                logger.exception("Erro inesperado no loop: %s", e)
                break

        self.conectado = False
        logger.info("Thread de leitura encerrada.")

    # ------------------------------------------------------------------
    # Packet decoder
    # ------------------------------------------------------------------

    def _parse_packet(self, header: int, data: bytes):
        pkt_id = header & 0x3F
        if pkt_id >= len(FLASH_READ_ADDR):
            return
        addr = FLASH_READ_ADDR[pkt_id]

        with self._lock:
            t = self._telemetry
            p = self._params  # write params without extra lock inside _lock

            # ── 0xE8  Tensão, Corrente ──────────────────────────────────
            if addr == 0xE8:
                t["volt"] = struct.unpack_from("<h", data, 0)[0] / 10.0
                t["curr"] = struct.unpack_from("<h", data, 4)[0] / 4.0
                t["power"] = t["volt"] * t["curr"]

            # ── 0xE2  RPM, Hall, Erros, Throttle, Torque, Status ────────
            elif addr == 0xE2:
                # RPM
                rpm = abs(struct.unpack_from("<h", data, 6)[0])
                t["rpm"] = 0 if rpm < 20 else rpm

                # Throttle position (mV → V)
                raw_thr = struct.unpack_from("<H", data, 0)[0]
                if raw_thr < 6000:
                    t["throttle"] = round(raw_thr / 1000.0, 2)

                # Motion / direction flags  (data[0])
                t["forward"] = bool(data[0] & 0x01)
                t["reverse"] = bool(data[0] & 0x02)
                t["motion"] = bool(data[0] & 0x20)

                # Hall sensors — phase active flags (data[1] bits 0,1,2)
                t["hall_a"] = bool(data[1] & 0x01)
                t["hall_b"] = bool(data[1] & 0x02)
                t["hall_c"] = bool(data[1] & 0x04)

                # Brake flag (data[3] bit 7)
                t["brake"] = bool(data[3] & 0x80) if len(data) > 3 else False

                # Error code (highest-priority active bit)
                new_err = _decode_error(data)
                t["error"] = new_err
                if new_err != 0 and new_err != self._last_error_code:
                    desc = ERROS_FARDRIVER.get(new_err, f"Código {new_err}")
                    self.error_history.append(
                        {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "code": new_err,
                            "desc": desc,
                        }
                    )
                    logger.warning(
                        "[ERRO] %s — %s", datetime.now().strftime("%H:%M:%S"), desc
                    )
                self._last_error_code = new_err

                # Torque  (fardriver.hpp → GetTorque)
                # data[8-9]=unkE6 (D-axis current), data[10-11]=unkE7 (Q-axis)
                unk_e6 = struct.unpack_from("<h", data, 8)[0]
                unk_e7 = struct.unpack_from("<h", data, 10)[0]
                coeff = self._torque_coeff if self._torque_coeff > 0 else 8192
                torque_raw = ((unk_e6 * unk_e6 + unk_e7 * unk_e7) << 9) // coeff
                t["torque"] = round(torque_raw / 10.0, 1)

            # ── 0xF4  Temperatura Motor, SOC ─────────────────────────────
            elif addr == 0xF4:
                val = struct.unpack_from("<h", data, 0)[0]
                if -20 < val < 200:
                    t["temp_motor"] = val
                soc = data[3] if len(data) > 3 else 0
                if 0 <= soc <= 100:
                    t["batt_soc"] = soc

            # ── 0xD6  Temperatura Controladora ───────────────────────────
            elif addr == 0xD6:
                val = struct.unpack_from("<h", data, 10)[0]
                if -20 < val < 150:
                    t["temp_mosfet"] = val

            # ── 0xBE  TorqueCoeff ────────────────────────────────────────
            elif addr == 0xBE:
                coeff = struct.unpack_from("<H", data, 10)[0]
                if 256 <= coeff <= 16384:
                    self._torque_coeff = coeff
                    logger.debug("TorqueCoeff → %d", coeff)

            # ── 0x0C  Addr0C: PhaseOffset, ZeroBattCoeff, PID ───────────
            elif addr == 0x0C:
                val = struct.unpack_from("<h", data, 0)[0] / 10.0
                if -360.0 <= val <= 360.0:
                    t["phase_offset"] = val
                # Store PID params
                p["start_ki"] = data[6]
                p["mid_ki"] = data[7]
                p["max_ki"] = data[8]
                p["start_kp"] = data[9]
                p["mid_kp"] = data[10]
                p["max_kp"] = data[11]
                p["zero_batt_coeff"] = struct.unpack_from("<h", data, 2)[0]
                p["full_batt_coeff"] = struct.unpack_from("<h", data, 4)[0]

            # ── 0x12  Addr12: PolePairs, RatedSpeed/Power/Voltage ────────
            elif addr == 0x12:
                p["pole_pairs"] = data[4]
                p["max_speed"] = struct.unpack_from("<H", data, 6)[0]
                p["rated_power"] = struct.unpack_from("<H", data, 8)[0]
                p["rated_voltage"] = struct.unpack_from("<H", data, 10)[0] / 10.0

            # ── 0x18  Addr18: RatedSpeed, MaxLineCurr, Throttle/WeakA ───
            elif addr == 0x18:
                p["rated_speed"] = struct.unpack_from("<H", data, 0)[0]
                p["max_line_curr"] = struct.unpack_from("<H", data, 2)[0] / 4.0
                cfg26l = data[4]
                p["follow_config"] = cfg26l & 0x03
                p["throttle_response"] = (cfg26l >> 2) & 0x03
                p["weaka"] = (cfg26l >> 4) & 0x03

            # ── 0x06  Addr06: ThrottleLow/High, TempSensor, Direction ───
            elif addr == 0x06:
                p["throttle_low"] = data[6] / 20.0
                p["throttle_high"] = data[7] / 20.0
                cfg11l = data[10]
                p["temp_sensor"] = (cfg11l >> 1) & 0x07
                cfg11h = data[11]
                p["direction"] = (cfg11h >> 7) & 0x01

            # ── 0x1E  Addr1E: LowVolProtect ──────────────────────────────
            elif addr == 0x1E:
                p["low_vol_protect"] = struct.unpack_from("<H", data, 2)[0] / 10.0

            # ── 0x24  Addr24: MaxPhaseCurr, BackSpeed, LowSpeed ─────────
            elif addr == 0x24:
                p["max_phase_curr"] = struct.unpack_from("<H", data, 4)[0] / 4.0
                p["back_speed"] = struct.unpack_from("<H", data, 8)[0]
                p["low_speed"] = struct.unpack_from("<H", data, 10)[0]

            # ── 0x30  Addr30: StopBackCurr, MaxBackCurr ──────────────────
            elif addr == 0x30:
                p["stop_back_curr"] = struct.unpack_from("<H", data, 0)[0]
                p["max_back_curr"] = struct.unpack_from("<H", data, 2)[0]

            # ── 0x82  Addr82: Hardware/Software version, Temp limits ─────
            elif addr == 0x82:
                p["motor_temp_protect"] = data[4]
                p["motor_temp_restore"] = data[5]
                p["mos_temp_protect"] = data[6]
                p["mos_temp_restore"] = data[7]
                hw = data[9]
                p["hardware_version"] = chr(hw) if 32 <= hw <= 126 else "?"
                sw = data[10]
                p["software_version"] = chr(sw) if 32 <= sw <= 126 else "?"

            # ── 0x88  Addr88: Current-limit ratio table (low RPM) ────────
            elif addr == 0x88:
                labels = [
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
                ]
                rt = p.get("ratio_table", {})
                for i, lbl in enumerate(labels):
                    rt[lbl] = data[i]
                p["ratio_table"] = rt

            # ── 0x8E  Addr8E: Current-limit ratio table (high RPM) + regen start
            elif addr == 0x8E:
                labels_h = [
                    "6000",
                    "6500",
                    "7000",
                    "7500",
                    "8000",
                    "8500",
                    "9000",
                    "max",
                ]
                rt = p.get("ratio_table", {})
                nrt = p.get("nratio_table", {})
                for i, lbl in enumerate(labels_h):
                    rt[lbl] = data[i]
                for i in range(4):
                    nrt[f"n{i}"] = struct.unpack_from("b", data, 8 + i)[0]
                p["ratio_table"] = rt
                p["nratio_table"] = nrt

            # ── 0x94  Addr94: Regen table (mid) ──────────────────────────
            elif addr == 0x94:
                nrt = p.get("nratio_table", {})
                for i in range(12):
                    nrt[f"n{i + 4}"] = struct.unpack_from("b", data, i)[0]
                p["nratio_table"] = nrt

            # ── 0x9A  Addr9A: Regen table (end) + AN/LM ──────────────────
            elif addr == 0x9A:
                nrt = p.get("nratio_table", {})
                for i in range(4):
                    nrt[f"n{i + 16}"] = struct.unpack_from("b", data, i)[0]
                p["nratio_table"] = nrt
                p["AN"] = data[4] & 0x0F
                p["LM"] = data[5] & 0x1F

    # ------------------------------------------------------------------
    # Public read API
    # ------------------------------------------------------------------

    def ler_dados(self) -> dict:
        """Thread-safe snapshot of real-time telemetry."""
        with self._lock:
            return self._telemetry.copy()

    def get_params(self) -> dict:
        """Thread-safe snapshot of flash parameters (populated after connect)."""
        with self._lock:
            return self._params.copy()

    # ------------------------------------------------------------------
    # Internal write helpers
    # ------------------------------------------------------------------

    def _compute_crc16(self, payload: bytes):
        a, b = 0x3C, 0x7F
        for byte in payload:
            i = a ^ byte
            a = b ^ CRC_TABLE_HI[i]
            b = CRC_TABLE_LO[i]
        return a, b

    def _write_address(self, addr: int, data: bytes, flags: int = 1) -> bool:
        """
        Modern Write-Address-Direct protocol.

        Packet structure:
            0xAA | byte1 | addr | addr | data[N] | crc_a | crc_b

        byte1 = (compute_length & 0x3F) | (flags << 6)
        compute_length = total_len - 2   (excludes CRC bytes)

        flags=1 : normal parameter write
        flags=3 : SysCmd (autolearn, factory reset, gather data)
        """
        if not self.conectado or not self.serial_obj:
            return False

        total_len = 4 + len(data) + 2
        compute_length = total_len - 2
        byte1 = (compute_length & 0x3F) | ((flags & 0x03) << 6)
        payload = bytes([0xAA, byte1, addr, addr]) + data
        crc_a, crc_b = self._compute_crc16(payload)
        packet = payload + bytes([crc_a, crc_b])

        try:
            self.serial_obj.write(packet)
            logger.debug("[WR] addr=0x%02X flags=%d data=%s", addr, flags, data.hex())
            return True
        except serial.SerialException as e:
            logger.error("Falha ao escrever addr=0x%02X: %s", addr, e)
            return False

    def _enviar_pacote(self, cmd, subcmd, val1, val2) -> bool:
        """Legacy protocol — checksum only. Used for keep-alive."""
        if not self.conectado or not self.serial_obj:
            return False
        try:
            p = [cmd, (~cmd) & 0xFF, subcmd, val1, val2]
            cs, not_cs = calculate_checksum(p)
            self.serial_obj.write(bytes([0xAA] + p + [cs, not_cs]))
            return True
        except serial.SerialException as e:
            logger.error("Falha no pacote legado: %s", e)
            return False

    # ------------------------------------------------------------------
    # Public write API
    # ------------------------------------------------------------------

    def enviar_configuracoes(self, config_dict: dict) -> bool:
        """
        Write parameters using Write-Address-Direct (flags=1).

        Supported keys:
            linha_a   → word 0x19  MaxLineCurr    (A × 4, uint16 LE)
            fase_a    → word 0x2D  MaxPhaseCurr   (A × 4, uint16 LE)
            regen_a   → word 0x30  StopBackCurr + 0x31 MaxBackCurr
            polos     → word 0x14  PolePairs
            throttle  → word 0x1A  cfg26l bits[3:2]
            weaka     → word 0x1A  cfg26l bits[5:4]
        """
        if not self.conectado:
            return False

        sent = 0

        if "linha_a" in config_dict:
            raw = int(round(config_dict["linha_a"] * 4)) & 0xFFFF
            if self._write_address(PARAM_ADDR["linha_a"], struct.pack("<H", raw)):
                sent += 1
                logger.info(
                    "[WRITE] MaxLineCurr=%d A (raw=%d)", config_dict["linha_a"], raw
                )

        if "fase_a" in config_dict:
            raw = int(round(config_dict["fase_a"] * 4)) & 0xFFFF
            if self._write_address(PARAM_ADDR["fase_a"], struct.pack("<H", raw)):
                sent += 1
                logger.info(
                    "[WRITE] MaxPhaseCurr=%d A (raw=%d)", config_dict["fase_a"], raw
                )

        if "regen_a" in config_dict:
            stop_raw = int(config_dict["regen_a"]) & 0xFFFF
            max_raw = int(round(config_dict["regen_a"] * 1.25)) & 0xFFFF
            if self._write_address(
                PARAM_ADDR["regen_stop"], struct.pack("<H", stop_raw)
            ):
                sent += 1
            if self._write_address(PARAM_ADDR["regen_max"], struct.pack("<H", max_raw)):
                sent += 1

        if "polos" in config_dict:
            pole = int(config_dict["polos"]) & 0xFF
            if self._write_address(PARAM_ADDR["polos"], bytes([pole, 0x59])):
                sent += 1
                logger.info("[WRITE] PolePairs=%d", pole)

        if "throttle" in config_dict or "weaka" in config_dict:
            t_bits = int(config_dict.get("throttle", 0)) & 0x03
            w_bits = int(config_dict.get("weaka", 0)) & 0x03
            cfg26l = (w_bits << 4) | (t_bits << 2)
            if self._write_address(PARAM_ADDR["throttle_weaka"], bytes([cfg26l, 0x00])):
                sent += 1
                logger.info(
                    "[WRITE] ThrottleResponse=%d WeakA=%d (cfg26l=0x%02X)",
                    t_bits,
                    w_bits,
                    cfg26l,
                )

        if sent == 0:
            logger.warning("enviar_configuracoes: nenhum parâmetro reconhecido.")
            return False

        logger.info("enviar_configuracoes: %d escrita(s).", sent)
        return True

    def iniciar_autolearn(self) -> bool:
        """SysCmd 0x02 — start rotor auto-learn. Controller beeps 2 short + 1 long."""
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Auto-Learn START")
        return self._write_address(
            PARAM_ADDR["syscmd"], bytes([0x88, SYSCMD["autolearn"]]), flags=3
        )

    def cancelar_autolearn(self) -> bool:
        """SysCmd 0x03 — cancel auto-learn in progress."""
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Auto-Learn CANCEL")
        return self._write_address(
            PARAM_ADDR["syscmd"], bytes([0x88, SYSCMD["cancel_learn"]]), flags=3
        )

    def restaurar_fabrica(self) -> bool:
        """SysCmd 0x08 — factory reset. Verified packet: AA C6 A0 A0 88 08 C5 09."""
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Factory Reset")
        return self._write_address(
            PARAM_ADDR["syscmd"], bytes([0x88, SYSCMD["factory_reset"]]), flags=3
        )

    def iniciar_coleta_dados(self) -> bool:
        """SysCmd 0x06 — start 2048-sample acceleration data capture."""
        if not self.conectado:
            return False
        logger.info("[SYSCMD] Gather Data START")
        return self._write_address(
            PARAM_ADDR["syscmd"], bytes([0x88, SYSCMD["gather_data"]]), flags=3
        )
