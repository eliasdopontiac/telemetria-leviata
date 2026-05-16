import csv
import json
import threading
from datetime import datetime
import os

from config import CSV_FILE


class TelemetryBackend:
    def __init__(self, ui_callback):
        self.ui_callback = ui_callback
        self.lock = threading.Lock()
        # Cabeçalho expandido para v2026
        self._header = [
            "ts", "fonte", "gps_hora", "v_solar", "i_solar", "pot_solar",
            "soc", "v_bat", "i_liq", "rpm", "i_motor", "t_motor", "t_ctrl",
            "vel", "lat", "lon", "sats", "falha_ctrl", "pkt_seq", "sig_lora", "sig_lte"
        ]
        self._init_csv()

    def _init_csv(self):
        try:
            file_exists = os.path.isfile(CSV_FILE)
            with open(CSV_FILE, "a", newline="") as f:
                if not file_exists or os.path.getsize(CSV_FILE) == 0:
                    csv.writer(f).writerow(self._header)
        except Exception as e:
            print(f"Erro ao inicializar CSV: {e}")

    def process(self, payload, source):
        if not payload:
            return

        try:
            if isinstance(payload, (bytes, bytearray)):
                payload = payload.decode("utf-8", errors="ignore")

            payload = payload.strip().replace("\x00", "")

            if not payload.startswith("{") or not payload.endswith("}"):
                return

            data = json.loads(payload)
            ts = datetime.now().strftime("%H:%M:%S")
            
            # Extração segura conforme nova estrutura sugerida
            s = data.get("solar", {})
            b = data.get("bateria", {})
            p = data.get("prop", {})
            n = data.get("nav", {})
            sig = data.get("sinal", {})

            # Preparar linha para o CSV (mantendo ordem do self._header)
            row = [
                ts,
                source,
                n.get("gps_hora", "--:--:--"),
                s.get("tensao", 0),
                s.get("corrente", 0),
                s.get("pot", 0),
                b.get("soc", 0),
                b.get("tensao_bat", 0),
                b.get("corrente_liq", 0),
                p.get("rpm", 0),
                p.get("i_motor", 0),
                p.get("t_motor", 0),
                p.get("t_ctrl", 0),
                n.get("vel", 0),
                n.get("lat", 0),
                n.get("lon", 0),
                n.get("gps_satelites", 0),
                p.get("fardriver_falha", 0),
                sig.get("lora_pacotes", 0),
                sig.get("lora", 0),
                sig.get("lte", 0),
            ]

            with self.lock:
                with open(CSV_FILE, "a", newline="") as f:
                    csv.writer(f).writerow(row)
            
            self.ui_callback(data, source)
        except json.JSONDecodeError:
            if len(payload) > 5:
                print(f"JSON inválido de {source}: {payload}")
        except Exception as e:
            print(f"Erro ao processar ({source}): {e}")
