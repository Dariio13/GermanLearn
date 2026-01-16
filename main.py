import flet as ft
import datos 
from deep_translator import GoogleTranslator

def main(page: ft.Page):
    page.title = "Aprende Alemán"
    page.window_width = 400
    page.window_height = 750 # Un poquito más alto para que quepa todo bien
    page.theme_mode = "light" 
    
    # --- HELPER: EL SEMÁFORO DE COLORES ---
    def obtener_color(texto_aleman):
        if not texto_aleman: return ft.colors.BLACK
        texto = texto_aleman.lower()
        
        if texto.startswith("der "):
            return ft.colors.BLUE
        elif texto.startswith("die "):
            return ft.colors.PINK_600 
        elif texto.startswith("das "):
            return ft.colors.GREEN
        else:
            return ft.colors.BLACK

    # --- VARIABLES ---
    palabra_actual = datos.obtener_palabra_random()
    aleman_actual = palabra_actual[0]
    espanol_actual = palabra_actual[1]

    # --- LÓGICA: JUEGO ---
    def logica_juego(e):
        nonlocal aleman_actual, espanol_actual
        
        if text_palabra.data == "aleman":
            # MOSTRAR ESPAÑOL
            text_palabra.value = espanol_actual
            text_palabra.color = ft.colors.BLACK
            text_palabra.weight = ft.FontWeight.NORMAL
            text_palabra.data = "espanol"
            boton_juego.text = "Siguiente Palabra"
        else:
            # MOSTRAR ALEMÁN
            nueva = datos.obtener_palabra_random()
            aleman_actual = nueva[0]
            espanol_actual = nueva[1]
            
            text_palabra.value = aleman_actual
            text_palabra.color = obtener_color(aleman_actual) 
            text_palabra.weight = ft.FontWeight.BOLD 
            text_palabra.data = "aleman"
            boton_juego.text = "Revelar Traducción"
            
        page.update()

    # --- LÓGICA: GESTIÓN (TRADUCCIÓN Y GUARDADO) ---
    
    def traducir_texto(e):
        """Toma el texto en Español y lo traduce al Alemán automáticamente"""
        texto_espanol = input_espanol.value
        
        if not texto_espanol:
            page.snack_bar = ft.SnackBar(ft.Text("Escribe algo en español primero"))
            page.snack_bar.open = True
            page.update()
            return

        try:
            # Traducimos ES -> DE
            traductor = GoogleTranslator(source='es', target='de')
            traduccion = traductor.translate(texto_espanol)
            
            # Ponemos el resultado en el campo de Alemán (Con mayúscula inicial)
            input_aleman.value = traduccion.capitalize()
            input_aleman.update()
            
            # Feedback visual pequeño
            page.snack_bar = ft.SnackBar(ft.Text("¡Traducción realizada!"), duration=1000)
            page.snack_bar.open = True
            page.update()
            
        except Exception as ex:
            print(f"Error: {ex}")
            page.snack_bar = ft.SnackBar(ft.Text("Error de conexión al traducir"))
            page.snack_bar.open = True
            page.update()

    def guardar_palabra(e):
        val_aleman = input_aleman.value.strip()
        val_espanol = input_espanol.value.strip()

        # 1. Validar vacíos
        if not val_aleman or not val_espanol:
            page.snack_bar = ft.SnackBar(ft.Text("Faltan campos por llenar"), bgcolor="orange")
            page.snack_bar.open = True
            page.update()
            return

        # 2. VALIDAR DUPLICADOS (Nueva función)
        # Usamos la función existe_palabra que agregaste a datos.py
        if datos.existe_palabra(val_aleman):
            page.snack_bar = ft.SnackBar(
                ft.Text(f"⚠️ La palabra '{val_aleman}' YA EXISTE en la base de datos."), 
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            return

        # 3. Guardar si todo está bien
        datos.agregar_palabra(val_aleman, val_espanol)
        
        # Limpiamos inputs
        input_aleman.value = ""
        input_espanol.value = ""
        
        # Actualizamos tabla
        cargar_tabla() 
        
        page.snack_bar = ft.SnackBar(ft.Text("¡Palabra guardada con éxito!"), bgcolor="green")
        page.snack_bar.open = True
        page.update()

    def cargar_tabla():
        tabla_datos.rows.clear()
        todas = datos.obtener_todas()
        
        # Invertimos la lista para ver las nuevas arriba (opcional, pero útil)
        todas_invertidas = list(reversed(todas))

        for p in todas_invertidas:
            color_fila = obtener_color(p[1]) 
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(p[1], color=color_fila, weight="bold")), # Alemán
                    ft.DataCell(ft.Text(p[2])), # Español
                    ft.DataCell(
                        ft.IconButton(
                            icon=ft.icons.DELETE, 
                            icon_color="red",
                            data=p[0], 
                            on_click=borrar_item
                        )
                    ),
                ]
            )
            tabla_datos.rows.append(row)
        page.update()

    def borrar_item(e):
        id_a_borrar = e.control.data 
        datos.borrar_palabra(id_a_borrar)
        cargar_tabla() 
        page.snack_bar = ft.SnackBar(ft.Text("Palabra eliminada"))
        page.snack_bar.open = True
        page.update()

    # --- UI COMPONENTES ---
    
    # PESTAÑA 1 (JUEGO)
    color_inicial = obtener_color(aleman_actual)
    text_palabra = ft.Text(
        value=aleman_actual, size=35, color=color_inicial, 
        weight=ft.FontWeight.BOLD, data="aleman", text_align=ft.TextAlign.CENTER
    )
    boton_juego = ft.ElevatedButton(text="Revelar Traducción", on_click=logica_juego)
    
    vista_juego = ft.Column(
        [
            ft.Icon(name=ft.icons.SCHOOL, size=50, color=ft.colors.BLUE_GREY),
            ft.Container(height=30),
            text_palabra,
            ft.Container(height=30),
            boton_juego,
            ft.Container(height=20),
            ft.Text("Azul=Masculino | Rosa=Femenino | Verde=Neutro", size=12, color="grey")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # PESTAÑA 2 (AGREGAR INTELIGENTE)
    # Reordenamos: Primero Español, luego botón traducir, luego Alemán
    input_espanol = ft.TextField(label="Español (Ej: El gato)", width=160)
    
    boton_traducir = ft.IconButton(
        icon=ft.icons.ARROW_FORWARD, 
        icon_color="blue", 
        tooltip="Traducir automáticamente",
        on_click=traducir_texto
    )
    
    input_aleman = ft.TextField(label="Alemán (Automático)", width=160)
    
    fila_inputs = ft.Row(
        [
            input_espanol, 
            boton_traducir, 
            input_aleman
        ], 
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    tabla_datos = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Alemán")),
            ft.DataColumn(ft.Text("Español")),
            ft.DataColumn(ft.Text("")),
        ],
        rows=[],
        heading_row_height=40,
        data_row_min_height=40
    )
    
    vista_agregar = ft.Column(
        [
            ft.Text("Agregar Vocabulario", size=20, weight="bold"),
            ft.Text("Escribe en español con artículo (Ej: La casa)", size=12, color="grey"),
            ft.Container(height=10),
            fila_inputs, # Fila con botón de traducción en medio
            ft.Container(height=10),
            ft.ElevatedButton(text="Guardar en Base de Datos", on_click=guardar_palabra),
            ft.Divider(),
            ft.Column([tabla_datos], scroll=ft.ScrollMode.ADAPTIVE, height=350) 
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # TABS
    t = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="Jugar", icon=ft.icons.GAMEPAD, content=ft.Container(content=vista_juego, padding=20, alignment=ft.alignment.center)),
            ft.Tab(text="Lista", icon=ft.icons.LIST, content=ft.Container(content=vista_agregar, padding=20)),
        ],
        expand=1,
    )

    page.add(t)
    cargar_tabla()

ft.app(target=main)