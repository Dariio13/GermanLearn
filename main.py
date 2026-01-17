import flet as ft
from vistas.menu import VistaMenu
from vistas.juego import VistaJuego
import datos

def main(page: ft.Page):
    page.title = "Alemán Master Modular"
    page.window_width = 400
    page.window_height = 600
    page.theme_mode = "light"
    page.padding = 0

    # Inicializamos DB
    datos.init_db()

    def ir_al_menu():
        page.controls.clear()
        
        # --- EL CAMBIO ESTÁ AQUÍ ---
        # Asignamos expand=True a la vista para que ocupe todo el alto
        menu = VistaMenu(fn_jugar=ir_al_juego)
        menu.expand = True 
        
        page.add(menu)
        page.update()

    def ir_al_juego(modo, nivel=None):
        page.controls.clear()
        
        # --- EL CAMBIO ESTÁ AQUÍ ---
        # Lo mismo para el juego, expand=True obliga a detectar clics en toda la pantalla
        juego = VistaJuego(page, modo, nivel, fn_volver=ir_al_menu)
        juego.expand = True 
        
        page.add(juego)
        page.update()

    ir_al_menu()

ft.app(target=main)