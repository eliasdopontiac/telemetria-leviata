
import os, re
b_path = r'Telemetria_2026\estação base\backend.py'
d_path = r'Telemetria_2026\estação base\dashboard.py'
with open(b_path, 'r', encoding='utf-8') as f: b = f.read()
if 'lat_int' not in b:
    b = b.replace('"sats", "proa", "hdop", "v_sist"', '"sats", "proa", "hdop", "lat_int", "lon_int", "v_sist"')
    b = b.replace('n = data.get("nav", {})', 'n = data.get("nav", {})\n            n_int = data.get("nav_int", {})')
    b = b.replace('n.get("hdop", 0),\n                v_sist,', 'n.get("hdop", 0),\n                n_int.get("lat", 0),\n                n_int.get("lon", 0),\n                v_sist,')
    with open(b_path, 'w', encoding='utf-8') as f: f.write(b)
with open(d_path, 'r', encoding='utf-8') as f: d = f.read()
if 'txt_gps_status' not in d:
    d = d.replace('txt_hdop = ft.Text("HDOP: —", size=13, weight="w500", color=config.MUTED)', 'txt_hdop = ft.Text("HDOP: —", size=13, weight="w500", color=config.MUTED)\n    txt_gps_status = ft.Text("GPS: AGUARDANDO", size=11, weight="bold", color=config.MUTED)')
    d = d.replace('ft.Row([txt_lat, txt_lon, txt_proa, txt_hdop], spacing=15, alignment="center")', 'ft.Column([ft.Row([txt_lat, txt_lon, txt_proa, txt_hdop], spacing=15, alignment="center"), txt_gps_status], horizontal_alignment="center")')
    d = d.replace('def to_f(v, default=0.0):', 'n_int = data.get("nav_int", {})\n                    def to_f(v, default=0.0):')
    m_code = '''
                    lat, lon = to_f(n.get("lat", 0)), to_f(n.get("lon", 0))
                    lat_i, lon_i = to_f(n_int.get("lat", 0)), to_f(n_int.get("lon", 0))
                    gps_ativo_lat, gps_ativo_lon = lat, lon
                    if lat != 0 and lat_i != 0:
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
                        txt_gps_status.color = config.MUTED
                    if gps_ativo_lat != 0 and gps_ativo_lon != 0:
                        gs.lat, gs.lon = gps_ativo_lat, gps_ativo_lon
                        marker.coordinates = fm.MapLatitudeLongitude(gps_ativo_lat, gps_ativo_lon)
                        if gs.auto_center:
                            map_control.center = fm.MapLatitudeLongitude(gps_ativo_lat, gps_ativo_lon)
                            try: map_control.update()
                            except: pass
                        txt_lat.value = f"LAT: {gps_ativo_lat:.6f}"
                        txt_lon.value = f"LON: {gps_ativo_lon:.6f}"
'''
    d = re.sub(r'lat, lon = to_f\(n\.get\("lat", 0\)\), to_f\(n\.get\("lon", 0\)\).*?txt_lon\.value = f"LON: \{lon:\.6f\}"', m_code, d, flags=re.DOTALL)
    with open(d_path, 'w', encoding='utf-8') as f: f.write(d)

