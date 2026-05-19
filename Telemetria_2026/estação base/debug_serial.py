
import os

dashboard_path = r'Telemetria_2026\estação base\dashboard.py'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = f.read()

if 'if line: backend.process(line, "LoRa")' in d:
    d = d.replace(
        'if line: backend.process(line, "LoRa")',
        'if line:\n                            print(f"[SERIAL RX] Lendo: {line[:50]}...")\n                            backend.process(line, "LoRa")'
    )
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(d)
    print('Debug adicionado')

