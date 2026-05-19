import os

config_path = r"Telemetria_2026\estação base\config.py"

with open(config_path, "r", encoding="utf-8") as f:
    config_content = f.read()

# Substitui mosquitto por hivemq
new_content = config_content.replace(
    'test.mosquitto.org',
    'broker.hivemq.com'
)

# Adiciona o novo tópico se estiver diferente
new_content = new_content.replace(
    'leviata/telemetria',
    'leviata/telemetria/race'
)

# Fix para evitar substituir "race/race" caso rode duas vezes
new_content = new_content.replace(
    'leviata/telemetria/race/race',
    'leviata/telemetria/race'
)

with open(config_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Broker atualizado no config.py!")
