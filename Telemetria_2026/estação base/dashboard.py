import asyncio
import threading
import time
import os
import json
from collections import deque
from datetime import datetime

import config
import flet as ft
import flet_charts as fch
import flet_map as fm
import paho.mqtt.client as mqtt
import serial
import serial.tools.list_ports
from backend import TelemetryBackend
from ui_components import (
    make_badge,
    make_card,
    make_serial_control,
    make_signal_bars,
    metric_block,
    big_metric_block,
    section_label,
    update_signal_bars,
    make_status_led,
)


async def create_dashboard(page: ft.Page):
    # --- ESTADO GLOBAL ---
    vel_history = deque([0.0]*200, maxlen=200)
    pot_history = deque([0.0]*200, maxlen=200)
    curr_motor_history = deque([0.0]*200, maxlen=200)
    curr_bat_history = deque([0.0]*200, maxlen=200)
    
    class GPSState:
        lat = -3.11902; lon = -60.02173; auto_center = True
    gs = GPSState()
    
    packet_state = {"received": 0, "last_seq": 0, "lost": 0}
    last_data = {"data": None, "source": None}
    serial_active = False; stop_serial = threading.Event()
    mqtt_active = False; stop_mqtt = threading.Event()
    mqtt_client_ref = [None]; serial_port_ref = [None]

    # --- WIDGETS ---
    txt_gps_time = ft.Text("--:--:--", size=14, weight="bold", color=config.PRIMARY)
    dot_lte_row, dot_lte = make_status_led("LTE", config.RED)
    txt_lte_perc = ft.Text("0%", size=10, weight="bold", color=config.MUTED)
    dot_lora_row, dot_lora = make_status_led("LORA", config.RED)
    txt_lora_perc = ft.Text("0%", size=10, weight="bold", color=config.MUTED)

    txt_vel_kmh = ft.Text("0.0", size=45, weight="bold", color=config.PRIMARY)
    txt_vel_nos = ft.Text("0.0 kt", size=14, weight="bold", color=config.MUTED)
    txt_sats = ft.Text("🛰️ -- Satélites", size=11, color=config.MUTED)
    txt_soc = ft.Text("0", size=45, weight="bold", color=config.GREEN)
    bar_soc = ft.ProgressBar(value=0, color=config.GREEN, bgcolor=config.BORDER_COLOR, bar_height=8, border_radius=5)
    txt_autonomia_tempo = ft.Text("--h --m", size=35, weight="bold", color=config.FG)
    txt_autonomia_dist = ft.Text("-- km", size=12, color=config.MUTED, weight="bold")
    txt_pot = ft.Text("0", size=32, weight="bold", color=config.AMBER)
    txt_i_liq = ft.Text("0.0", size=32, weight="bold", color=config.FG)
    txt_t_motor = ft.Text("—", size=32, weight="bold", color=config.FG)
    txt_t_ctrl = ft.Text("—", size=32, weight="bold", color=config.FG)
    txt_v_panel = ft.Text("—", size=22, weight="bold", color=config.FG)
    txt_i_panel = ft.Text("—", size=22, weight="bold", color=config.FG)
    txt_v_bat = ft.Text("—", size=22, weight="bold", color=config.FG)
    txt_rpm = ft.Text("—", size=24, weight="bold", color=config.FG)
    txt_i_motor = ft.Text("—", size=24, weight="bold", color=config.FG)
    fault_row, fault_led = make_status_led("SISTEMA OK", config.GREEN)
    bars_lora = make_signal_bars(); bars_lte = make_signal_bars()
    txt_pkt_loss = ft.Text("Loss: 0%", size=11, color=config.MUTED, weight="bold")
    txt_raw_sig = ft.Text("RSSI: -- | CSQ: --", size=10, color=config.MUTED)
    txt_lat = ft.Text("—", size=13, weight="w500", color=config.MUTED)
    txt_lon = ft.Text("—", size=13, weight="w500", color=config.MUTED)
    txt_ts = ft.Text("Aguardando telemetria...", size=11, color=config.MUTED)

    # --- GRÁFICOS ---
    chart_vel_series = fch.LineChartData(points=[fch.LineChartDataPoint(i, 0) for i in range(200)], stroke_width=3, color=config.PRIMARY, curved=True)
    chart_pot_series = fch.LineChartData(points=[fch.LineChartDataPoint(i, 0) for i in range(200)], stroke_width=3, color=config.AMBER, curved=True)
    chart_cm_series = fch.LineChartData(points=[fch.LineChartDataPoint(i, 0) for i in range(200)], stroke_width=3, color=config.RED, curved=True)
    chart_cb_series = fch.LineChartData(points=[fch.LineChartDataPoint(i, 0) for i in range(200)], stroke_width=3, color=config.BLUE, curved=True)

    def make_analysis_chart(series, color, title, max_y, interval):
        return ft.Column([
            ft.Text(title, size=13, color=color, weight="bold"),
            fch.LineChart(
                data_series=[series], expand=True, height=250, min_y=0, max_y=max_y, border=None,
                horizontal_grid_lines=fch.ChartGridLines(color=ft.Colors.with_opacity(0.1, config.FG)),
                left_axis=fch.ChartAxis(show_labels=True, label_size=50, label_spacing=interval), 
                bottom_axis=fch.ChartAxis(show_labels=False),
            )
        ], expand=True)

    chart_v = make_analysis_chart(chart_vel_series, config.PRIMARY, "VELOCIDADE (km/h)", 40, 10)
    chart_p = make_analysis_chart(chart_pot_series, config.AMBER, "POTÊNCIA SOLAR (W)", 600, 100)
    chart_m = make_analysis_chart(chart_cm_series, config.RED, "CORRENTE MOTOR (A)", 100, 20)
    chart_b = make_analysis_chart(chart_cb_series, config.BLUE, "CORRENTE BATERIA (A)", 100, 20)

    # --- MAPA ---
    marker = fm.Marker(content=ft.Icon(ft.Icons.LOCATION_ON, color=config.RED, size=35), coordinates=fm.MapLatitudeLongitude(gs.lat, gs.lon))
    map_control = fm.Map(expand=True, initial_center=fm.MapLatitudeLongitude(gs.lat, gs.lon), initial_zoom=16,
                         layers=[fm.TileLayer(url_template="http://tile.openstreetmap.org/{z}/{x}/{y}.png"), fm.MarkerLayer(markers=[marker])])

    # --- CONTROLES ---
    async def refresh_ports(e=None):
        ports = serial.tools.list_ports.comports()
        port_dropdown.options = [ft.dropdown.Option(p.device) for p in ports]
        if not port_dropdown.value and ports: port_dropdown.value = ports[0].device
        page.update()

    async def toggle_serial(e):
        nonlocal serial_active
        if not serial_active:
            if not port_dropdown.value: return
            serial_active = True; stop_serial.clear(); btn_connect.text = "STOP LORA"
            btn_connect.bgcolor = ft.Colors.with_opacity(0.2, config.RED); port_dropdown.disabled = True
            asyncio.create_task(serial_worker_task(port_dropdown.value))
        else:
            serial_active = False; stop_serial.set()
            if serial_port_ref[0]:
                try: serial_port_ref[0].close()
                except: pass
            btn_connect.text = "START LORA"; btn_connect.bgcolor = ft.Colors.with_opacity(0.1, config.GREEN)
            port_dropdown.disabled = False; dot_lora.bgcolor = config.RED
        page.update()

    txt_mqtt_status = ft.Text("DESCONECTADO", size=10, weight="bold", color=config.RED)
    async def toggle_mqtt(e):
        nonlocal mqtt_active
        if not mqtt_active:
            mqtt_active = True; stop_mqtt.clear()
            btn_mqtt.text = "STOP MQTT"; btn_mqtt.bgcolor = ft.Colors.with_opacity(0.2, config.RED)
            txt_mqtt_status.value = "CONECTANDO..."; txt_mqtt_status.color = config.YELLOW; page.update()
            asyncio.create_task(mqtt_worker())
        else:
            mqtt_active = False; stop_mqtt.set()
            if mqtt_client_ref[0]:
                try: mqtt_client_ref[0].disconnect(); mqtt_client_ref[0].loop_stop()
                except: pass
            btn_mqtt.text = "START MQTT"; btn_mqtt.bgcolor = ft.Colors.with_opacity(0.1, config.PRIMARY)
            txt_mqtt_status.value = "DESCONECTADO"; txt_mqtt_status.color = config.RED
            dot_lte.bgcolor = config.RED; page.update()
        page.update()

    btn_mqtt = ft.ElevatedButton("START MQTT", icon=ft.Icons.CLOUD_SYNC_ROUNDED, color=config.FG, bgcolor=ft.Colors.with_opacity(0.1, config.PRIMARY), on_click=toggle_mqtt)
    serial_row, port_dropdown, btn_connect = make_serial_control(toggle_serial, refresh_ports)
    btn_connect.text = "START LORA"

    # --- LOOP DE ATUALIZAÇÃO DA UI ---
    async def ui_refresh_loop():
        fault_blink = False
        while True:
            try:
                if last_data["data"]:
                    data = last_data["data"]; source = last_data["source"]
                    n = data.get("nav", {}); s = data.get("solar", {}); b = data.get("bateria", {}); p = data.get("prop", {}); sig = data.get("sinal", {})
                    def to_f(v, default=0.0):
                        try: return float(v) if v is not None else default
                        except: return default
                    vel = to_f(n.get("vel", n.get("velocidade", 0)))
                    pot = to_f(s.get("pot", s.get("potencia", 0)))
                    soc = to_f(b.get("soc", 0)); i_motor = to_f(p.get("i_motor", p.get("corrente", 0)))
                    i_liq = to_f(b.get("corrente_liq", to_f(s.get("corrente", 0)) - i_motor))
                    tm = to_f(p.get("t_motor", p.get("temp_motor", 0))); tc = to_f(p.get("t_ctrl", p.get("temp_ctrl", 0)))
                    txt_gps_time.value = n.get("gps_hora", "--:--:--")
                    txt_vel_kmh.value = f"{vel:.1f}"; txt_vel_nos.value = f"{(vel * 0.539957):.1f} kt"
                    txt_sats.value = f"🛰️ {n.get('gps_satelites', 0)} Satélites"
                    lat, lon = to_f(n.get("lat", 0)), to_f(n.get("lon", 0))
                    if lat != 0 and lon != 0:
                        gs.lat, gs.lon = lat, lon; marker.coordinates = fm.MapLatitudeLongitude(lat, lon)
                        if gs.auto_center:
                            map_control.center = fm.MapLatitudeLongitude(lat, lon)
                            try: map_control.update()
                            except: pass
                        txt_lat.value = f"LAT: {lat:.6f}"; txt_lon.value = f"LON: {lon:.6f}"
                    txt_pot.value = str(round(pot)); txt_v_panel.value = f"{to_f(s.get('tensao', 0)):.1f}"; txt_i_panel.value = f"{to_f(s.get('corrente', 0)):.1f}"
                    txt_soc.value = f"{round(soc)}"; bar_soc.value = max(0.0, min(1.0, soc / 100))
                    bar_soc.color = config.GREEN if soc > 40 else (config.YELLOW if soc > 20 else config.RED)
                    txt_i_liq.value = f"{i_liq:.1f}"; txt_i_liq.color = config.SUCCESS if i_liq >= 0 else config.RED
                    if i_liq >= 0:
                        txt_autonomia_tempo.value = "∞ h"; txt_autonomia_tempo.color = config.SUCCESS; txt_autonomia_dist.value = "SOLAR POSITIVO"
                    else:
                        dreno = abs(i_liq); ah_disponivel = config.BAT_CAPACITY_AH * (soc / 100.0)
                        horas = ah_disponivel / dreno if dreno > 0.05 else 0
                        if horas > 0:
                            h = int(horas); m = int((horas - h) * 60); txt_autonomia_tempo.value = f"{h:02d}h {m:02d}m"
                            txt_autonomia_tempo.color = config.RED if horas < 1 else config.FG
                            txt_autonomia_dist.value = f"EST: {vel * horas:.1f} KM"
                        else:
                            txt_autonomia_tempo.value = "00h 00m"; txt_autonomia_dist.value = "DRENO ALTO"
                    txt_t_motor.value = f"{tm:.0f}°C"; txt_t_ctrl.value = f"{tc:.0f}°C"
                    txt_t_motor.color = config.RED if tm > 65 else (config.YELLOW if tm > 50 else config.FG)
                    txt_t_ctrl.color = config.RED if tc > 60 else (config.YELLOW if tc > 45 else config.FG)
                    txt_rpm.value = str(round(to_f(p.get("rpm", 0)))); txt_i_motor.value = f"{i_motor:.1f}"; txt_v_bat.value = f"{to_f(b.get('tensao_bat', b.get('tensao', 0))):.1f}"
                    is_fault = p.get("fardriver_falha", 0)
                    if is_fault:
                        fault_led.bgcolor = config.RED if fault_blink else config.BG_COLOR
                        fault_row.controls[1].value = "FALHA CRÍTICA"; fault_row.controls[1].color = config.RED
                    else:
                        fault_led.bgcolor = config.GREEN; fault_row.controls[1].value = "SISTEMA OK"; fault_row.controls[1].color = config.MUTED
                    fault_blink = not fault_blink
                    vel_history.append(vel); pot_history.append(pot); curr_motor_history.append(i_motor); curr_bat_history.append(abs(i_liq))
                    chart_vel_series.points = [fch.LineChartDataPoint(i, v) for i, v in enumerate(vel_history)]
                    chart_pot_series.points = [fch.LineChartDataPoint(i, v) for i, v in enumerate(pot_history)]
                    chart_cm_series.points = [fch.LineChartDataPoint(i, v) for i, v in enumerate(curr_motor_history)]
                    chart_cb_series.points = [fch.LineChartDataPoint(i, v) for i, v in enumerate(curr_bat_history)]
                    csq = to_f(sig.get("lte", 0)); lte_quality = min(100, max(0, int((csq / 31.0) * 100)))
                    rssi = to_f(sig.get("lora", 0)); lora_quality = min(100, max(0, int(((rssi + 120) / 90.0) * 100)))
                    txt_lte_perc.value = f"{lte_quality}%"; txt_lora_perc.value = f"{lora_quality}%"
                    update_signal_bars(bars_lora, lora_quality); update_signal_bars(bars_lte, lte_quality)
                    
                    async def blink_led(led):
                        led.bgcolor = config.SUCCESS; page.update(); await asyncio.sleep(0.3); led.bgcolor = config.RED; page.update()
                    active_led = dot_lte if source == "LTE" else dot_lora
                    asyncio.create_task(blink_led(active_led))
                    txt_ts.value = f"Sync: {datetime.now().strftime('%H:%M:%S')} | Fonte: {source}"
                    last_data["data"] = None; page.update()
            except Exception as e: print(f"Erro Loop UI: {e}")
            await asyncio.sleep(0.1)

    # --- ABA TELEMETRIA ---
    tab_telemetria = ft.ResponsiveRow([
        ft.Column([
            # TIER 1: ALTURA FIXA 170
            ft.ResponsiveRow([
                make_card(col={"md": 4}, height=170, content=ft.Column([section_label("VELOCIDADE", ft.Icons.SPEED_ROUNDED), ft.Row([txt_vel_kmh, ft.Text("km/h", size=14, color=config.MUTED)], spacing=5, vertical_alignment="end"), txt_vel_nos, txt_sats], horizontal_alignment="center", spacing=2, alignment="center")),
                make_card(col={"md": 4}, height=170, content=ft.Column([section_label("BATERIA", ft.Icons.BATTERY_CHARGING_FULL_ROUNDED), ft.Row([txt_soc, ft.Text("%", size=14, color=config.MUTED)], spacing=5, vertical_alignment="end"), bar_soc], horizontal_alignment="center", spacing=15, alignment="center")),
                make_card(col={"md": 4}, height=170, content=ft.Column([section_label("AUTONOMIA", ft.Icons.TIMELAPSE_ROUNDED), ft.Container(txt_autonomia_tempo, padding=ft.Padding(0, 5, 0, 5)), txt_autonomia_dist], horizontal_alignment="center", spacing=2, alignment="center")),
            ], spacing=10),
            
            # TIER 2: ALTURA FIXA 140
            ft.ResponsiveRow([
                make_card(col={"md": 6}, height=140, content=ft.Row([ft.Column([section_label("Balanço Líquido", ft.Icons.SWAP_VERT_ROUNDED), ft.Row([txt_i_liq, ft.Text("A", size=14, color=config.MUTED)], spacing=5, vertical_alignment="end")], expand=True, alignment="center"), ft.VerticalDivider(width=1, color=config.BORDER_COLOR), ft.Column([section_label("Potência Solar", ft.Icons.WB_SUNNY_ROUNDED), ft.Row([txt_pot, ft.Text("W", size=14, color=config.MUTED)], spacing=5, vertical_alignment="end")], expand=True, alignment="center")], alignment="spaceAround")),
                make_card(col={"md": 6}, height=140, content=ft.Row([ft.Column([section_label("Temp Motor", ft.Icons.THERMOSTAT_ROUNDED), txt_t_motor], expand=True, horizontal_alignment="center", alignment="center"), ft.VerticalDivider(width=1, color=config.BORDER_COLOR), ft.Column([section_label("Temp Ctrl", ft.Icons.THERMOSTAT_ROUNDED), txt_t_ctrl], expand=True, horizontal_alignment="center", alignment="center")], alignment="spaceAround")),
            ], spacing=10),

            # TIER 3: ALTURA FIXA 140
            ft.ResponsiveRow([
                make_card(col={"md": 6}, height=140, content=ft.Column([section_label("Propulsão", ft.Icons.SETTINGS_ROUNDED), ft.Row([metric_block("Giro (RPM)", txt_rpm, ""), metric_block("Consumo", txt_i_motor, "A")], spacing=25, alignment="center")], spacing=10, alignment="center")),
                make_card(col={"md": 6}, height=140, content=ft.Column([section_label("Segurança", ft.Icons.SHIELD_ROUNDED), ft.Row([metric_block("V Solar", txt_v_panel, "V"), metric_block("V Bat", txt_v_bat, "V")], spacing=25, alignment="center"), fault_row], spacing=10, alignment="center")),
            ], spacing=10),

            # TIER 4: DIAGNÓSTICO
            make_card(height=110, content=ft.Column([section_label("Diagnóstico de Rede", ft.Icons.WIFI_TETHERING_ROUNDED), ft.Row([ft.Column([ft.Text("LTE", size=10, color=config.MUTED), ft.Row(bars_lte, spacing=2)], spacing=5), ft.VerticalDivider(width=20), ft.Column([ft.Text("LORA", size=10, color=config.MUTED), ft.Row(bars_lora, spacing=2)], spacing=5), ft.VerticalDivider(width=20), ft.Column([txt_pkt_loss, txt_raw_sig], spacing=2, alignment="center")], alignment="start")], alignment="center")),
        ], col={"md": 7}, spacing=10),
        
        ft.Column([make_card(height=605, content=ft.Column([ft.Row([section_label("Navegação Espacial", ft.Icons.MAP_ROUNDED), ft.Row([ft.Text("AUTO-CENTRO", size=9, color=config.MUTED, weight="bold"), ft.Switch(value=True, on_change=lambda e: setattr(gs, "auto_center", e.control.value))], spacing=5)], alignment="spaceBetween"), ft.Container(map_control, border_radius=10, clip_behavior="hardEdge", expand=True, bgcolor="#1a1a1a"), ft.Row([txt_lat, txt_lon], spacing=20, alignment="center")], spacing=10))], col={"md": 5}, spacing=10),
    ], spacing=10)

    tab_analise = ft.Column([ft.Row([make_card(content=chart_v, expand=True, height=400), make_card(content=chart_p, expand=True, height=400)], spacing=10), ft.Row([make_card(content=chart_m, expand=True, height=400), make_card(content=chart_b, expand=True, height=400)], spacing=10)], spacing=10, scroll="adaptive")

    async def refresh_ports(e=None):
        ports = serial.tools.list_ports.comports()
        port_dropdown.options = [ft.dropdown.Option(p.device) for p in ports]
        if not port_dropdown.value and ports: port_dropdown.value = ports[0].device
        page.update()

    async def toggle_serial(e):
        nonlocal serial_active
        if not serial_active:
            if not port_dropdown.value: return
            serial_active = True; stop_serial.clear(); btn_connect.text = "STOP LORA"
            btn_connect.bgcolor = ft.Colors.with_opacity(0.2, config.RED); port_dropdown.disabled = True
            asyncio.create_task(serial_worker_task(port_dropdown.value))
        else:
            serial_active = False; stop_serial.set()
            if serial_port_ref[0]:
                try: serial_port_ref[0].close()
                except: pass
            btn_connect.text = "START LORA"; btn_connect.bgcolor = ft.Colors.with_opacity(0.1, config.GREEN)
            port_dropdown.disabled = False; dot_lora.bgcolor = config.RED
        page.update()

    serial_row, port_dropdown, btn_connect = make_serial_control(toggle_serial, refresh_ports)
    btn_connect.text = "START LORA"
    content_area = ft.Container(content=tab_telemetria, expand=True, padding=10)

    def switch_tab(e):
        if e.control.data == "tele":
            btn_tele.bgcolor = config.PRIMARY_MUTED; btn_tele.color = config.PRIMARY
            btn_anal.bgcolor = "transparent"; btn_anal.color = config.MUTED; content_area.content = tab_telemetria
        else:
            btn_anal.bgcolor = config.PRIMARY_MUTED; btn_anal.color = config.PRIMARY
            btn_tele.bgcolor = "transparent"; btn_tele.color = config.MUTED; content_area.content = tab_analise
        page.update()

    btn_tele = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.DASHBOARD_ROUNDED, size=18), ft.Text("TELEMETRIA", weight="bold")], spacing=10), data="tele", on_click=switch_tab, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor=config.PRIMARY_MUTED, color=config.PRIMARY))
    btn_anal = ft.TextButton(content=ft.Row([ft.Icon(ft.Icons.INSERT_CHART_ROUNDED, size=18), ft.Text("ANÁLISE", weight="bold")], spacing=10), data="anal", on_click=switch_tab, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor="transparent", color=config.MUTED))
    nav_bar = ft.Container(content=ft.Row([btn_tele, btn_anal], spacing=10), padding=5, bgcolor=ft.Colors.with_opacity(0.05, config.FG), border_radius=10, border=ft.Border.all(1, config.BORDER_COLOR))

    header = ft.Row([
        ft.Column([ft.Row([ft.Icon(ft.Icons.DIRECTIONS_BOAT_ROUNDED, color=config.PRIMARY, size=32), ft.Text("LEVIATÃ v2026", size=24, weight="bold", color=config.FG)]),
                   ft.Row([ft.Text("HORA GPS:", size=11, color=config.MUTED), txt_gps_time], spacing=5)], spacing=0),
        ft.Container(content=ft.Row([
            ft.Column([btn_mqtt, txt_mqtt_status], horizontal_alignment="center", spacing=2),
            ft.VerticalDivider(width=1, color=config.BORDER_COLOR),
            serial_row,
            ft.VerticalDivider(width=1, color=config.BORDER_COLOR),
            ft.Row([ft.Column([dot_lte_row, txt_lte_perc], horizontal_alignment="center", spacing=2), ft.Column([dot_lora_row, txt_lora_perc], horizontal_alignment="center", spacing=2)], spacing=20)
        ], spacing=30), bgcolor=ft.Colors.with_opacity(0.03, config.FG), padding=ft.Padding(25, 8, 25, 8), border_radius=15, border=ft.Border.all(1, config.BORDER_COLOR)),
    ], alignment="spaceBetween")

    page.add(header, ft.Container(height=10), nav_bar, content_area, ft.Divider(height=1, color=config.BORDER_COLOR), ft.Container(content=ft.Row([txt_ts], alignment="center"), padding=10))
    page.on_disconnect = lambda e: os._exit(0)
    loop = asyncio.get_running_loop(); backend = TelemetryBackend(lambda d, s: None)
    def update_ui_bridge(data, source): last_data.update({"data": data, "source": source})
    backend.ui_callback = update_ui_bridge
    asyncio.create_task(ui_refresh_loop())

    async def serial_worker_task(port):
        def run_serial():
            try:
                ser = serial.Serial(port, config.BAUD_RATE, timeout=0.1); serial_port_ref[0] = ser
                while not stop_serial.is_set():
                    if ser.in_waiting:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if line: backend.process(line, "LoRa")
                    else: time.sleep(0.005)
                ser.close()
            except: pass
        await asyncio.to_thread(run_serial)

    async def mqtt_worker():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                txt_mqtt_status.value = "CONECTADO"; txt_mqtt_status.color = config.SUCCESS; page.update()
                client.subscribe(config.MQTT_TOPIC)
            else:
                txt_mqtt_status.value = f"ERRO {rc}"; txt_mqtt_status.color = config.RED; page.update()
        def on_message(client, userdata, message): backend.process(message.payload, "LTE")
        def run_mqtt():
            try:
                client = mqtt.Client(); client.on_connect = on_connect; client.on_message = on_message
                mqtt_client_ref[0] = client; client.connect(config.MQTT_BROKER, 1883, 60)
                while not stop_mqtt.is_set(): client.loop(0.1)
                client.disconnect()
            except: 
                txt_mqtt_status.value = "FALHA REDE"; txt_mqtt_status.color = config.RED; page.update()
        await asyncio.to_thread(run_mqtt)

    await refresh_ports()
