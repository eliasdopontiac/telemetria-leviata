import config
import flet as ft
from dashboard import create_dashboard


async def main(page: ft.Page):
    page.title = "Telemetria Leviatã v2026"
    page.bgcolor = config.BG_COLOR
    page.theme_mode = ft.ThemeMode.DARK
    
    # --- CONFIGURAÇÃO DE ÍCONE ---
    # Coloque um arquivo chamado 'icon.png' na mesma pasta do projeto
    # page.window_icon = "icon.png" 
    
    # Configurações de Janela
    page.window_width = 1300
    page.window_height = 950
    page.window_min_width = 1100
    page.window_min_height = 800
    page.padding = 24
    page.spacing = 0

    # Inicia o Dashboard
    await create_dashboard(page)


if __name__ == "__main__":
    ft.app(target=main)
