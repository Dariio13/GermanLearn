import flet as ft
from vistas.menu import VistaMenu
from vistas.juego import VistaJuego
import datos

def main(page: ft.Page):
    page.title = "Alemán Master"
    page.window_width = 600
    page.window_height = 700
    page.theme_mode = "light"
    page.padding = 0

    # Inicializamos DB
    datos.init_db()

    def ir_al_menu():
        # 1. Limpieza de seguridad (Mata dialogos fantasmas)
        page.dialog = None
        page.banner = None
        page.overlay.clear()
        
        # 2. Limpiar controles
        page.controls.clear()
        
        # 3. Crear el menú pasando AMBAS funciones
        # fn_jugar: Para ir a los juegos
        # fn_volver: Para que las sub-vistas (como Historias) sepan cómo volver aquí
        menu = VistaMenu(fn_jugar=ir_al_juego, fn_volver=ir_al_menu)
        menu.expand = True  # Esto asegura que los clics funcionen
        
        page.add(menu)
        page.update()

    def ir_al_juego(modo, nivel=None):
        page.controls.clear()
        juego = VistaJuego(page, modo, nivel, fn_volver=ir_al_menu)
        juego.expand = True 
        page.add(juego)
        page.update()

    ir_al_menu()

ft.app(target=main)