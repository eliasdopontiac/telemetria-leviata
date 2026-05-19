
import os

config_path = r'Telemetria_2026\estação base\config.py'
with open(config_path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('MQTT_TOPIC = "barco/telemetria/+"', 'MQTT_TOPIC = "leviata/telemetria/race"')

with open(config_path, 'w', encoding='utf-8') as f:
    f.write(c)

