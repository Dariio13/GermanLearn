import flet as ft
import datos
import cerebro  # Importamos cerebro para el generador a la carta
import json
import threading

def vista_lectura(page: ft.Page, fn_volver):
    page.title = "Lecciones con IA"
    page.clean()

    # --- GENERADOR A LA CARTA (Funciones) ---
    def abrir_creador_historias(e):
        # Campo de texto para el tema
        txt_tema = ft.TextField(label="¿De qué quieres la historia?", hint_text="Ej: Un dragón en Berlín, Batman comprando pan...")
        txt_nivel = ft.Dropdown(
            label="Nivel", 
            options=[ft.dropdown.Option("A1"), ft.dropdown.Option("A2"), ft.dropdown.Option("B1"), ft.dropdown.Option("B2")],
            value="A1"
        )
        loading = ft.ProgressBar(width=400, color="amber", bgcolor="#222222", visible=False)
        btn_crear = ft.ElevatedButton("✨ Crear con IA", on_click=lambda _: generar_y_guardar())

        def generar_y_guardar():
            if not txt_tema.value: return
            
            # UI de carga
            btn_crear.disabled = True
            btn_crear.text = "Generando... (Espera 5s)"
            loading.visible = True
            page.update()

            # Función que corre en segundo plano para no congelar la app
            def tarea_ia():
                try:
                    contenido = cerebro.generar_leccion_historia(txt_nivel.value, txt_tema.value)
                    if contenido:
                        datos.guardar_leccion(txt_nivel.value, txt_tema.value, contenido)
                        # Cerramos dialogo y recargamos
                        dlg_crear.open = False
                        page.update()
                        cargar_menu_niveles() # Recargar lista
                        page.snack_bar = ft.SnackBar(ft.Text("¡Historia creada exitosamente!"))
                        page.snack_bar.open = True
                    else:
                        btn_crear.text = "Error. Intenta de nuevo."
                except Exception as ex:
                    print(ex)
                finally:
                    btn_crear.disabled = False
                    loading.visible = False
                    page.update()

            # Ejecutar en hilo separado
            threading.Thread(target=tarea_ia, daemon=True).start()

        dlg_crear = ft.AlertDialog(
            title=ft.Text("✨ Generador a la Carta"),
            content=ft.Column([
                ft.Text("Escribe un tema loco y la IA creará una lección única para ti."),
                txt_tema,
                txt_nivel,
                loading
            ], height=200, tight=True),
            actions=[btn_crear, ft.TextButton("Cancelar", on_click=lambda _: cerrar_dlg())],
        )
        
        def cerrar_dlg():
            dlg_crear.open = False
            page.update()

        page.dialog = dlg_crear
        dlg_crear.open = True
        page.update()

    # --- MOSTRAR HISTORIA CON QUIZ ---
    def mostrar_detalle_historia(leccion_id, contenido_json):
        data = json.loads(contenido_json)
        
        titulo = ft.Text(data["titulo"], size=24, weight="bold", text_align="center")
        
        # Pestañas existentes
        tab_historia = ft.Column([
            ft.Container(content=ft.Text(data["historia"], size=18, selectable=True), padding=20, bgcolor=ft.colors.BLUE_GREY_50, border_radius=10)
        ], scroll="auto")

        tab_traduccion = ft.Column([
            ft.Container(content=ft.Text(data["traduccion"], size=16, italic=True), padding=20, bgcolor=ft.colors.AMBER_50, border_radius=10)
        ])

        lista_vocab = ft.Column([ft.Text(p) for p in data.get("vocabulario_clave", [])])
        
        tab_profe = ft.Column([
            ft.Text("💡 Regla Gramatical:", weight="bold", color="blue"),
            ft.Text(data.get("punto_gramatical", "N/A"), weight="bold"),
            ft.Text(data.get("explicacion_gramatica", "N/A")),
            ft.Divider(),
            ft.Text("📚 Vocabulario Clave:", weight="bold", color="green"),
            lista_vocab
        ], scroll="auto")

        # --- NUEVA PESTAÑA: QUIZ ---
        items_quiz = []
        quiz_data = data.get("quiz", [])
        
        if not quiz_data:
            items_quiz.append(ft.Text("Esta lección no tiene quiz (es antigua)."))
        else:
            for idx, q in enumerate(quiz_data):
                items_quiz.append(ft.Text(f"{idx+1}. {q['pregunta']}", weight="bold"))
                
                # Grupo de opciones
                radio_group = ft.RadioGroup(content=ft.Column([
                    ft.Radio(value=str(i), label=op) for i, op in enumerate(q['opciones'])
                ]))
                
                # Texto de feedback (Correcto/Incorrecto)
                txt_feedback = ft.Text("", weight="bold")
                
                # Botón verificar individual
                def verificar_respuesta(e, correcta=q['respuesta_correcta'], fb=txt_feedback, rg=radio_group):
                    if rg.value == str(correcta):
                        fb.value = "✅ ¡Correcto!"
                        fb.color = "green"
                    else:
                        fb.value = "❌ Incorrecto"
                        fb.color = "red"
                    page.update()

                btn_check = ft.ElevatedButton("Verificar", on_click=verificar_respuesta)
                
                items_quiz.extend([radio_group, btn_check, txt_feedback, ft.Divider()])

        # --- CORRECCIÓN ---
        # 1. Creamos la columna SIN padding
        columna_quiz = ft.Column(items_quiz, scroll="auto")

        # 2. La metemos dentro de un Container que SÍ tiene padding
        tab_quiz = ft.Container(content=columna_quiz, padding=20)

        # Tabs container
        tabs_contenido = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="🇩🇪 Historia", content=tab_historia),
                ft.Tab(text="🇪🇸 Traducción", content=tab_traduccion),
                ft.Tab(text="👨‍🏫 Explicación", content=tab_profe),
                ft.Tab(text="📝 Quiz", content=tab_quiz), # <--- NUEVA TAB
            ],
            expand=1,
        )

        btn_volver_lista = ft.ElevatedButton("⬅ Volver a la lista", on_click=lambda _: cargar_menu_niveles())

        page.clean()
        page.add(
            btn_volver_lista,
            titulo,
            ft.Divider(),
            ft.Container(content=tabs_contenido, expand=True)
        )
        page.update()

    # --- LISTA DE LECCIONES ---
    def cargar_lista_por_nivel(nivel):
        lecciones = datos.obtener_lecciones_por_nivel(nivel)
        columna_items = ft.Column(spacing=10, scroll="auto", expand=True)

        if not lecciones:
            columna_items.controls.append(ft.Text(f"No hay historias para {nivel}. ¡Crea una!", color="grey"))
        else:
            for leccion in lecciones:
                id_lec, tema, contenido, completa = leccion
                card = ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.BOOK, color="blue"),
                            title=ft.Text(tema, weight="bold"),
                            subtitle=ft.Text(f"Nivel {nivel}"),
                            on_click=lambda e, id=id_lec, c=contenido: mostrar_detalle_historia(id, c)
                        ), padding=10
                    )
                )
                columna_items.controls.append(card)
        return ft.Container(content=columna_items, padding=10)

    # --- MENÚ PRINCIPAL DE LECCIONES ---
    def cargar_menu_niveles():
        page.clean()
        
        header = ft.Row([
            ft.IconButton(ft.icons.HOME, icon_color="blue", tooltip="Ir al Inicio", on_click=lambda _: fn_volver()),
            ft.Text("Biblioteca IA", size=24, weight="bold"),
            ft.Container(expand=True), # Espaciador
            ft.ElevatedButton("✨ Crear Historia", icon=ft.icons.AUTO_AWESOME, bgcolor="indigo", color="white", on_click=abrir_creador_historias)
        ], alignment="center")

        tabs_niveles = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="A1", content=cargar_lista_por_nivel("A1")),
                ft.Tab(text="A2", content=cargar_lista_por_nivel("A2")),
                ft.Tab(text="B1", content=cargar_lista_por_nivel("B1")),
                ft.Tab(text="B2", content=cargar_lista_por_nivel("B2")),
            ],
            expand=1
        )

        page.add(header, tabs_niveles)
        page.update()

    cargar_menu_niveles()

# Prueba independiente
if __name__ == "__main__":
    ft.app(target=lambda page: vista_lectura(page, lambda: print("Volver")))