import flet as ft
from config import BORDER_COLOR, CARD_COLOR, FG, GREEN, MUTED, RED, YELLOW, PRIMARY


def make_card(content, **kwargs):
    side = ft.BorderSide(1, BORDER_COLOR)
    return ft.Container(
        content=content,
        bgcolor=CARD_COLOR,
        border=ft.Border(side, side, side, side),
        border_radius=12,
        padding=20,
        **kwargs,
    )


def section_label(text, icon=None):
    items = []
    if icon:
        items.append(ft.Icon(icon, size=14, color=PRIMARY))
    items.append(
        ft.Text(text.upper(), size=11, color=MUTED, weight="bold")
    )
    return ft.Row(items, spacing=8)


def metric_block(label, value_ref, unit):
    return ft.Column(
        [
            ft.Text(label, size=11, color=MUTED, weight="w500"),
            ft.Row(
                [
                    value_ref,
                    ft.Text(unit, size=12, color=MUTED, weight="w400"),
                ],
                spacing=4,
                vertical_alignment="end",
            ),
        ],
        spacing=4,
    )


def big_metric_block(label, value_ref, unit, icon=None, color=FG, subtitle_ref=None):
    value_ref.size = 42
    value_ref.weight = "bold"
    value_ref.color = color
    
    col_items = [
        ft.Text(label.upper(), size=12, color=MUTED, weight="w600"),
        ft.Row(
            [
                value_ref,
                ft.Text(unit, size=18, color=MUTED, weight="w500"),
            ],
            spacing=8,
            vertical_alignment="end",
        ),
    ]
    if subtitle_ref:
        col_items.append(subtitle_ref)
    
    if icon:
        return ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, size=30, color=color),
                    bgcolor=ft.Colors.with_opacity(0.1, color),
                    padding=15,
                    border_radius=12,
                ),
                ft.Column(col_items, spacing=2),
            ],
            spacing=20,
        )
    return ft.Column(col_items, spacing=2)


def make_badge(text, text_color, bg_color):
    return ft.Container(
        content=ft.Text(text, size=11, color=text_color, weight="w600"),
        bgcolor=bg_color,
        border_radius=6,
        padding=ft.Padding(12, 4, 12, 4),
    )

def make_status_led(label, initial_color=GREEN):
    led = ft.Container(width=10, height=10, border_radius=5, bgcolor=initial_color)
    return ft.Row([
        led,
        ft.Text(label, size=11, color=MUTED, weight="bold")
    ], spacing=8), led


def make_signal_bars():
    return [
        ft.Container(width=4, height=h, border_radius=1, bgcolor=BORDER_COLOR)
        for h in [4, 7, 10, 13, 16]
    ]


def update_signal_bars(bars, quality):
    filled = round((quality / 100) * len(bars))
    color = GREEN if quality >= 70 else (YELLOW if quality >= 35 else RED)
    for i, b in enumerate(bars):
        b.bgcolor = color if i < filled else BORDER_COLOR


def make_serial_control(on_toggle, on_refresh):
    port_dropdown = ft.Dropdown(
        label="PORTA SERIAL",
        hint_text="Selecione...",
        width=180,
        height=45,
        text_size=12,
        label_style=ft.TextStyle(size=10, color=MUTED, weight="w600"),
        border_color=BORDER_COLOR,
        focused_border_color=PRIMARY,
        color=FG,
        content_padding=ft.Padding(10, 0, 10, 0),
    )

    btn_connect = ft.ElevatedButton(
        "CONECTAR",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        color=FG,
        bgcolor=ft.Colors.with_opacity(0.1, GREEN),
        on_click=on_toggle,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )

    btn_refresh = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_color=MUTED,
        on_click=on_refresh,
        tooltip="Atualizar portas",
    )

    return (
        ft.Row(
            [port_dropdown, btn_refresh, btn_connect],
            spacing=10,
            vertical_alignment="center",
        ),
        port_dropdown,
        btn_connect,
    )
