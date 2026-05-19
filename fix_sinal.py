import os
import re

b_path = r\"Telemetria_2026\estação base\backend.py\"
with open(b_path, 'r', encoding='utf-8') as f:
    b = f.read()

b = b.replace(
    'sig.get("lora_pacotes", 0),\n                sig.get("lora", 0),\n                sig.get("lte", 0),',
    'sig.get("lora_pacotes", 0) if source == "LoRa" else 0,\n                sig.get("lora", 0) if source == "LoRa" else 0,\n                sig.get("lte", 0) if source == "LTE" else 0,'
)
with open(b_path, 'w', encoding='utf-8') as f:
    f.write(b)

d_path = r\"Telemetria_2026\estação base\dashboard.py\"
with open(d_path, 'r', encoding='utf-8') as f:
    d = f.read()

replacement = \"\"\"
                    if source == "LTE":
                        csq = to_f(sig.get("lte", 0)); lte_quality = min(100, max(0, int((csq / 31.0) * 100)))
                        txt_lte_perc.value = f"{lte_quality}%"
                        update_signal_bars(bars_lte, lte_quality)
                    
                    if source == "LoRa":
                        rssi = to_f(sig.get("lora", 0)); lora_quality = min(100, max(0, int(((rssi + 120) / 90.0) * 100)))
                        txt_lora_perc.value = f"{lora_quality}%"
                        update_signal_bars(bars_lora, lora_quality)
\"\"\"

d = re.sub(r'csq = to_f\(sig\.get\("lte".*?update_signal_bars\(bars_lte, lte_quality\)', replacement, d, flags=re.DOTALL)

with open(d_path, 'w', encoding='utf-8') as f:
    f.write(d)
