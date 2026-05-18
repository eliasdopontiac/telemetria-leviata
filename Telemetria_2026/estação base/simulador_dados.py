import time
import json
import random
from datetime import datetime

# Simula o envio de JSON no formato esperado pelo backend
def gerar_pacote_simulado():
    agora = datetime.now()
    
    # Variáveis flutuantes aleatórias para simular navegação
    rpm = random.randint(1200, 1500)
    vel = rpm * 0.015  # Relaciona vel com rpm
    proa = random.uniform(170, 190)
    hdop = random.uniform(0.8, 1.5)
    v_sist = random.uniform(3.9, 4.2)
    
    # Potência solar e carga do motor
    pot_solar = random.uniform(250, 350)
    i_motor = random.uniform(15, 25)
    
    pacote = {
        "solar": {
            "tensao": 46.5 + random.uniform(-0.5, 0.5),
            "corrente": pot_solar / 46.5,
            "pot": pot_solar
        },
        "bateria": {
            "soc": random.randint(75, 80),
            "tensao_bat": 51.2 - random.uniform(0.1, 0.5),
            "corrente_liq": (pot_solar / 46.5) - i_motor
        },
        "prop": {
            "rpm": rpm,
            "i_motor": i_motor,
            "t_motor": random.uniform(45, 55),
            "t_ctrl": random.uniform(35, 45),
            "fardriver_falha": 0 if random.random() > 0.05 else random.choice([1, 5, 8]) # 5% de chance de erro
        },
        "nav": {
            "vel": vel,
            "lat": -3.119 + random.uniform(-0.001, 0.001),
            "lon": -60.021 + random.uniform(-0.001, 0.001),
            "gps_satelites": random.randint(8, 12),
            "gps_hora": agora.strftime("%H:%M:%S"),
            "proa": proa,
            "hdop": hdop
        },
        "sinal": {
            "lora_pacotes": random.randint(100, 200),
            "lora": random.randint(-90, -70),
            "lte": random.randint(15, 30)
        },
        "v_sist": v_sist
    }
    
    return json.dumps(pacote)

# Cria um arquivo para simular a porta serial virtual ou alimentar o backend
print("Gerador de Dados Simulado - Leviatã 2026")
print("Copiando 5 pacotes simulados...\n")

for i in range(5):
    print(f"--- Pacote {i+1} ---")
    print(gerar_pacote_simulado())
    print("\n")
    time.sleep(1)
