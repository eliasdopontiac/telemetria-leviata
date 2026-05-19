
import os

dashboard_path = r'Telemetria_2026\estação base\dashboard.py'

with open(dashboard_path, 'r', encoding='utf-8') as f:
    d = f.read()

if 'print(f"[MQTT RX]' not in d:
    d = d.replace(
        'def on_message(client, userdata, message): backend.process(message.payload, "LTE")',
        'def on_message(client, userdata, message):\n            print(f"[MQTT RX] Pacote Recebido: {len(message.payload)} bytes")\n            backend.process(message.payload, "LTE")'
    )
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(d)

