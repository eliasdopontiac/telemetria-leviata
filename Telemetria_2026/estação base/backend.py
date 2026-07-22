import csv
import json
import logging
import logging.handlers
import os
import re
import threading
from datetime import datetime

from config import CSV_FILE

# Configuração de logging com rotação
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_handler = logging.handlers.RotatingFileHandler(
    "telemetria_backend.log", maxBytes=1024 * 1024, backupCount=5, encoding="utf-8"
)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
log_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.addHandler(console_handler)


class TelemetryBackend:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.lock = threading.Lock()
        # Cabeçalho fixo e completo conforme solicitado
        self._header = [
            "timestamp_iso",
            "fonte",
            "gps_hora",
            "v_solar",
            "i_solar",
            "pot_solar",
            "soc",
            "v_bat",
            "i_liq",
            "rpm",
            "i_motor",
            "t_motor",
            "t_ctrl",
            "vel",
            "lat",
            "lon",
            "sats",
            "proa",
            "hdop",
            "lat_int",
            "lon_int",
            "v_sist",
            "falha_ctrl",
            "pkt_seq",
            "sig_lora",
            "sig_lte",
            "status_data",
        ]
        self._init_csv()

    def _init_csv(self):
        try:
            file_exists = os.path.isfile(CSV_FILE)
            with self.lock:
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    if not file_exists or os.path.getsize(CSV_FILE) == 0:
                        writer = csv.DictWriter(f, fieldnames=self._header)
                        writer.writeheader()
                        logger.info(f"Novo CSV criado: {CSV_FILE}")
        except Exception as e:
            logger.error(f"Falha ao inicializar CSV: {e}", exc_info=True)

    def _safe_float(self, val, default=0.0):
        try:
            return float(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    def process(self, payload, source):
        if not payload:
            return

        # Capture raw bytes for logging/diagnóstico
        original_payload = payload
        if isinstance(original_payload, (bytes, bytearray)):
            raw_bytes = bytes(original_payload)
        else:
            raw_bytes = str(original_payload).encode("utf-8", errors="ignore")

        raw_len = len(raw_bytes)
        ts_iso = datetime.now().isoformat()
        status_data = "valid"

        try:
            # Decodificação segura
            if isinstance(payload, (bytes, bytearray)):
                payload = payload.decode("utf-8", errors="ignore")

            payload_str = payload.strip().replace("\x00", "")

            # Diagnóstico de payload malformado
            if not payload_str.startswith("{") or not payload_str.endswith("}"):
                try:
                    raw_hex = raw_bytes[:64].hex()
                except Exception:
                    raw_hex = repr(raw_bytes[:64])
                logger.warning(
                    f"Payload inválido ({source}, {raw_len}b). RawHex: {raw_hex}"
                )
                return

            data = json.loads(payload_str)

            # Normalização e Schema Validation (campos esperados)
            s = data.get("solar", {})
            b = data.get("bateria", {})
            p = data.get("prop", {})
            n = data.get("nav", {})
            sig = data.get("sinal", {})
            n_int = data.get("nav_int", {})

            # Lógica de fallback de voltagem: bateria > solar
            v_bat = self._safe_float(b.get("tensao_bat"))
            if v_bat <= 0:
                v_bat = self._safe_float(s.get("tensao"))
                if v_bat > 0:
                    status_data = "solar_fallback"

            # Normalizar v_sist quando for string com conteúdo numérico
            raw_v_sist = data.get("v_sist")
            v_sist_val = raw_v_sist
            if isinstance(raw_v_sist, str):
                m = re.search(r"-?\d+(?:\.\d+)?", raw_v_sist)
                if m:
                    v_sist_val = m.group(0)
                else:
                    v_sist_val = None

            # Montagem do dicionário conforme colunas fixas
            row_dict = {
                "timestamp_iso": ts_iso,
                "fonte": source,
                "gps_hora": str(n.get("gps_hora", "--:--:--")),
                "v_solar": self._safe_float(s.get("tensao")),
                "i_solar": self._safe_float(s.get("corrente")),
                "pot_solar": self._safe_float(s.get("pot")),
                "soc": self._safe_float(b.get("soc")),
                "v_bat": v_bat,
                "i_liq": self._safe_float(b.get("corrente_liq")),
                "rpm": self._safe_float(p.get("rpm")),
                "i_motor": self._safe_float(p.get("i_motor")),
                "t_motor": self._safe_float(p.get("t_motor")),
                "t_ctrl": self._safe_float(p.get("t_ctrl")),
                "vel": self._safe_float(n.get("vel")),
                "lat": self._safe_float(n.get("lat")),
                "lon": self._safe_float(n.get("lon")),
                "sats": int(self._safe_float(n.get("gps_satelites"), 0)),
                "proa": self._safe_float(n.get("proa")),
                "hdop": self._safe_float(n.get("hdop")),
                "lat_int": self._safe_float(n_int.get("lat")),
                "lon_int": self._safe_float(n_int.get("lon")),
                "v_sist": self._safe_float(v_sist_val),
                "falha_ctrl": int(self._safe_float(p.get("fardriver_falha"), 0)),
                "pkt_seq": int(self._safe_float(sig.get("lora_pacotes"), 0)),
                "sig_lora": self._safe_float(sig.get("lora")),
                "sig_lte": self._safe_float(sig.get("lte")),
                "status_data": status_data,
            }

            # Validar ranges básicos de GPS/HDOP
            lat = row_dict.get("lat", 0.0)
            lon = row_dict.get("lon", 0.0)
            hdop = row_dict.get("hdop", 0.0)
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                hdop_f = float(hdop)
            except Exception:
                lat_f = lon_f = 0.0
                hdop_f = 99.9

            if (
                not (-90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0)
                or hdop_f < 0
                or hdop_f > 50
            ):
                row_dict["status_data"] = (
                    (row_dict["status_data"] + ";suspect_coords")
                    if row_dict["status_data"]
                    else "suspect_coords"
                )
                logger.warning(
                    f"GPS fora de range ou HDOP inválido: lat={lat}, lon={lon}, hdop={hdop} | RawHex: {raw_bytes[:64].hex()}"
                )

            # Escrita thread-safe via DictWriter
            with self.lock:
                with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=self._header)
                    writer.writerow(row_dict)

            # Envio para interface
            self.ui_callback(data, source)

        except json.JSONDecodeError as je:
            try:
                raw_hex = raw_bytes[:100].hex()
            except Exception:
                raw_hex = repr(raw_bytes[:100])
            logger.error(f"JSON Corrompido ({source}): {str(je)} | RawHex: {raw_hex}")
        except Exception as e:
            logger.exception(f"Erro crítico no processamento ({source}): {e}")
            # Tenta logar a linha como inválida se o DictWriter falhar
            try:
                with self.lock:
                    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
                        f.write(f"{ts_iso},{source},,,,,,,,,,,,,,,,,,,,,,,invalid\n")
            except:
                pass
