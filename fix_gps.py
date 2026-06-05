import os, re
path = r'Telemetria_2026\estação base\dashboard.py'
with open(path, 'r', encoding='utf-8') as f:
    d = f.read()

pattern = r'''                    if lat == 0 and lat_i != 0:
                        gps_ativo_lat, gps_ativo_lon = lat_i, lon_i
                        txt_gps_status\.value = "GPS: BACKUP LILYGO ATIVO"
                        txt_gps_status\.color = config\.AMBER
                    elif lat != 0 and lat_i != 0:
                        diff = abs\(lat - lat_i\) \+ abs\(lon - lon_i\)
                        if diff > 0\.002:
                            txt_gps_status\.value = "GPS: ALERTA DE DISCREPANCIA"
                            txt_gps_status\.color = config\.RED
                        else:
                            txt_gps_status\.value = "GPS: SINCRONIZADOS"
                            txt_gps_status\.color = config\.SUCCESS
                    else:
                        txt_gps_status\.value = "GPS: SEM SINAL"
                        txt_gps_status\.color = config\.MUTED'''

replacement = '''                    if lat != 0 and lat_i != 0:
                        diff = abs(lat - lat_i) + abs(lon - lon_i)
                        if diff > 0.002:
                            txt_gps_status.value = "GPS: ALERTA DE DISCREPANCIA"
                            txt_gps_status.color = config.RED
                        else:
                            txt_gps_status.value = "GPS: SINCRONIZADOS"
                            txt_gps_status.color = config.SUCCESS
                    elif lat != 0:
                        txt_gps_status.value = "GPS: SINAL OK"
                        txt_gps_status.color = config.SUCCESS
                    elif lat_i != 0:
                        gps_ativo_lat, gps_ativo_lon = lat_i, lon_i
                        txt_gps_status.value = "GPS: BACKUP LILYGO ATIVO"
                        txt_gps_status.color = config.AMBER
                    else:
                        txt_gps_status.value = "GPS: SEM SINAL"
                        txt_gps_status.color = config.MUTED'''

d_new = re.sub(pattern, replacement, d)
with open(path, 'w', encoding='utf-8') as f:
    f.write(d_new)

path_patch = r'Telemetria_2026\estação base\patch.py'
with open(path_patch, 'r', encoding='utf-8') as f:
    dp = f.read()
dp_new = re.sub(pattern, replacement, dp)
with open(path_patch, 'w', encoding='utf-8') as f:
    f.write(dp_new)

print("Updated via script!")
