import flet as ft
import time
import threading
import datos

class VistaJuego(ft.UserControl):
    def __init__(self, page, modo, nivel, fn_volver):
        super().__init__()
        self.page = page
        self.modo = modo
        self.nivel = nivel
        self.fn_volver = fn_volver 
        
        # Estado del juego
        self.sesion = []
        self.indice = 0
        self.puntos = 0
        self.tiempo = 60
        self.timer_activo = False

    def build(self):
        # --- UI ELEMENTS ---
        self.txt_contador = ft.Text("", color="blue")
        self.txt_palabra = ft.Text(size=30, weight="bold", text_align="center")
        self.txt_resultado = ft.Text("", size=16, weight="bold")
        
        self.btn_der = ft.ElevatedButton("", width=150, height=50, on_click=self.verificar)
        self.btn_die = ft.ElevatedButton("", width=150, height=50, on_click=self.verificar)
        self.btn_das = ft.ElevatedButton("", width=150, height=50, on_click=self.verificar)
        
        self.fila_opciones = ft.Row([self.btn_der, self.btn_die, self.btn_das], visible=False, alignment="center")
        self.btn_elegir = ft.ElevatedButton("Elegir Artículo", height=50, on_click=self.mostrar_opciones)
        self.btn_siguiente = ft.ElevatedButton("Siguiente ➡", visible=False, on_click=self.siguiente)

        # Layout
        return ft.Column([
            ft.Container(height=30),
            ft.Row([
                ft.IconButton(ft.icons.CLOSE, on_click=lambda _: self.volver_seguro()), 
                self.txt_contador
            ], alignment="spaceBetween"),
            ft.Divider(),
            ft.Container(height=20),
            ft.Icon(ft.icons.SPORTS_ESPORTS, size=40, color="orange"),
            self.txt_palabra,
            ft.Container(height=30),
            self.btn_elegir,
            self.fila_opciones,
            ft.Container(height=20),
            self.txt_resultado,
            self.btn_siguiente
        ], horizontal_alignment="center")

    def did_mount(self):
        self.iniciar_logica()

    # --- NUEVO: FUNCIÓN PARA SALIR DE FORMA SEGURA ---
    def volver_seguro(self):
        self.timer_activo = False # Matamos el timer antes de salir
        self.fn_volver()

    def iniciar_logica(self):
        if self.modo == "normal":
            self.sesion = datos.obtener_palabras_session(self.nivel, 10)
            self.txt_contador.value = f"Nivel {self.nivel}"
        elif self.modo == "hospital":
            self.sesion = datos.obtener_enfermas()
            self.txt_contador.value = f"Hospital: {len(self.sesion)}"
        elif self.modo == "blitz":
            self.sesion = datos.obtener_palabras_blitz(100)
            self.timer_activo = True
            threading.Thread(target=self.correr_timer, daemon=True).start()

        if not self.sesion:
            self.txt_palabra.value = "¡No hay palabras disponibles!"
            self.btn_elegir.disabled = True
        else:
            self.cargar_pregunta()
        self.update()

    def cargar_pregunta(self):
        self.txt_resultado.value = ""
        self.btn_siguiente.visible = False
        self.fila_opciones.visible = False
        self.btn_elegir.visible = True
        
        if self.modo == "blitz": 
            self.mostrar_opciones(None)
        
        for btn in [self.btn_der, self.btn_die, self.btn_das]:
            btn.disabled = False
            btn.style = ft.ButtonStyle(bgcolor=ft.colors.GREY_100, color="black")

        if self.indice < len(self.sesion):
            self.txt_palabra.value = self.sesion[self.indice][2] 
        else:
            self.terminar_sesion()
        self.update()

    def mostrar_opciones(self, e):
        palabra = self.sesion[self.indice][1] 
        partes = palabra.split(" ", 1)
        sustantivo = partes[1] if len(partes) > 1 else palabra
        
        self.btn_der.text = f"Der {sustantivo}"; self.btn_der.data = "Der " + sustantivo
        self.btn_die.text = f"Die {sustantivo}"; self.btn_die.data = "Die " + sustantivo
        self.btn_das.text = f"Das {sustantivo}"; self.btn_das.data = "Das " + sustantivo
        
        self.respuesta_correcta = palabra
        self.btn_elegir.visible = False
        self.fila_opciones.visible = True
        self.update()

    def verificar(self, e):
        # --- CORRECCIÓN 1: SI EL JUEGO TERMINÓ, IGNORAR CLICS ---
        if self.modo == "blitz" and (not self.timer_activo or self.tiempo <= 0):
            return

        btn = e.control
        es_correcto = (btn.data == self.respuesta_correcta)
        id_palabra = self.sesion[self.indice][0]

        if es_correcto:
            self.puntos += 1
            btn.style = ft.ButtonStyle(bgcolor=ft.colors.GREEN, color="white")
            self.txt_resultado.value = "¡Correcto!"
            self.txt_resultado.color = "green"
            datos.actualizar_progreso(id_palabra, "bien", self.modo)
            
            if self.modo == "blitz":
                self.tiempo += 2
                self.update(); time.sleep(0.5); self.siguiente(None); return
        else:
            btn.style = ft.ButtonStyle(bgcolor=ft.colors.RED, color="white")
            self.txt_resultado.value = f"Era: {self.respuesta_correcta}"
            self.txt_resultado.color = "red"
            datos.actualizar_progreso(id_palabra, "mal", self.modo)
            
            if self.modo == "blitz": 
                self.tiempo -= 5
                # --- CORRECCIÓN 2: VERIFICAR SI LA RESTA MATÓ EL JUEGO ---
                if self.tiempo <= 0:
                    self.tiempo = 0
                    self.terminar_sesion()
                    return

        # Bloquear botones
        self.btn_der.disabled = True; self.btn_die.disabled = True; self.btn_das.disabled = True
        self.btn_siguiente.visible = True
        self.update()

    def siguiente(self, e):
        self.indice += 1
        self.cargar_pregunta()

    def correr_timer(self):
        while self.tiempo > 0 and self.timer_activo:
            time.sleep(1)
            # --- CORRECCIÓN 3: VERIFICAR DE NUEVO ANTES DE RESTAR ---
            if not self.timer_activo: break
            
            self.tiempo -= 1
            if self.tiempo < 0: self.tiempo = 0 # Evitar negativos visuales
            
            self.txt_contador.value = f"🔥 {self.tiempo}s | Puntos: {self.puntos}"
            try: self.update()
            except: pass
            
        # Si salimos del bucle porque se acabó el tiempo (y no porque el usuario salió)
        if self.tiempo <= 0 and self.timer_activo:
            self.terminar_sesion()

    def terminar_sesion(self):
        self.timer_activo = False # Apagar bandera global
        
        # Bloquear todo visualmente
        self.btn_der.disabled = True
        self.btn_die.disabled = True
        self.btn_das.disabled = True
        self.btn_elegir.disabled = True
        try: self.update()
        except: pass

        mensaje = f"¡Tiempo fuera! Acertaste {self.puntos} palabras."

        # --- CORRECCIÓN AQUÍ: Función para cerrar antes de salir ---
        def cerrar_y_salir(e):
            dlg.open = False       # 1. Apagar el diálogo
            self.page.update()     # 2. Refrescar la pantalla (importante para que desaparezca)
            self.fn_volver()       # 3. Ahora sí, volver al menú

        dlg = ft.AlertDialog(
            title=ft.Text("Fin del Juego"), 
            content=ft.Text(mensaje),
            modal=True, 
            # Usamos nuestra nueva función en el botón
            actions=[ft.TextButton("Volver al Menú", on_click=cerrar_y_salir)]
        )
        
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()