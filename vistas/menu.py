import flet as ft
import datos
import vistas.lectura_ia as lectura_ia 

class VistaMenu(ft.UserControl):
    # 1. Aceptamos fn_volver en el constructor
    def __init__(self, fn_jugar, fn_volver):
        super().__init__()
        self.fn_jugar = fn_jugar 
        self.fn_volver = fn_volver # Guardamos la función maestra de volver

    def build(self):
        self.col_niveles = ft.Column(horizontal_alignment="center")
        self.txt_pacientes = ft.Text("0", size=30, weight="bold", color="red")
        self.btn_curar = ft.ElevatedButton("Entrar al Hospital 🏥", bgcolor="red", color="white")
        
        # Tabs container
        self.tabs = ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="Aprender", icon=ft.icons.SCHOOL, content=ft.Column([
                    ft.Container(height=60), 
                    self.col_niveles
                ], scroll="auto")),
                
                ft.Tab(text="Hospital", icon=ft.icons.LOCAL_HOSPITAL, content=self.vista_hospital()),
                
                ft.Tab(text="Blitz", icon=ft.icons.FLASH_ON, content=self.vista_blitz()),

                ft.Tab(text="Historias", icon=ft.icons.AUTO_STORIES, content=self.vista_historias()),
            ],
            expand=1
        )
        return self.tabs

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        stats = datos.obtener_estadisticas()
        
        # Cargar Niveles
        self.col_niveles.controls.clear()
        row1 = ft.Row([self.btn_nivel("A1", stats), self.btn_nivel("A2", stats)], alignment="center")
        row2 = ft.Row([self.btn_nivel("B1", stats), self.btn_nivel("B2", stats)], alignment="center")
        row3 = ft.Row([self.btn_nivel("C1", stats), self.btn_nivel("C2", stats)], alignment="center")
        self.col_niveles.controls.extend([row1, ft.Container(height=10), row2, ft.Container(height=10), row3])
        
        # Cargar Hospital
        num = stats.get("hospital_count", 0)
        self.txt_pacientes.value = f"{num} Pacientes"
        self.btn_curar.disabled = (num == 0)
        self.btn_curar.on_click = lambda _: self.fn_jugar("hospital")
        
        self.update()

    def btn_nivel(self, nivel, stats):
        try:
            prog = stats.get(nivel, 0)
            txt = stats.get(f"{nivel}_txt", "0/0")
        except: prog=0; txt="Err"
        
        return ft.Container(
            content=ft.Column([
                ft.Text(f"Nivel {nivel}", color="white", weight="bold"),
                ft.ProgressBar(value=prog, color="white", bgcolor=ft.colors.with_opacity(0.3, "black")),
                ft.Text(txt, color="white", size=10)
            ], alignment="center"),
            width=140, height=90, bgcolor="blue", border_radius=10, padding=10, ink=True,
            on_click=lambda _: self.fn_jugar("normal", nivel)
        )

    def vista_hospital(self):
        return ft.Column([
            ft.Container(height=50),
            ft.Icon(ft.icons.LOCAL_HOSPITAL, size=80, color="red"),
            self.txt_pacientes,
            ft.Text("Pacientes recuperándose", text_align="center"),
            ft.Container(height=20),
            self.btn_curar
        ], horizontal_alignment="center", spacing=20)

    def vista_blitz(self):
        return ft.Column([
            ft.Container(height=50),
            ft.Icon(ft.icons.FLASH_ON, size=80, color="amber"),
            ft.Text("Modo BLITZ", size=30, weight="bold"),
            ft.Text("¡Contra el reloj!", text_align="center"),
            ft.Container(height=20),
            ft.ElevatedButton("¡INICIAR! ⚡", bgcolor="amber", color="black", 
                              on_click=lambda _: self.fn_jugar("blitz"))
        ], horizontal_alignment="center", spacing=20)

    def vista_historias(self):
        # Ya no necesitamos definir 'volver_al_inicio' aquí adentro
        # porque 'self.fn_volver' (que viene de main.py) ya sabe cómo hacerlo perfecto.
        
        return ft.Column([
            ft.Container(height=50),
            ft.Icon(ft.icons.AUTO_STORIES, size=80, color="indigo"),
            ft.Text("Historias IA", size=30, weight="bold"),
            ft.Text("Mejora tu lectura con historias\ngeneradas por Inteligencia Artificial.", text_align="center"),
            ft.Container(height=20),
            
            ft.ElevatedButton(
                "Entrar a la Biblioteca 📖", 
                bgcolor="indigo", 
                color="white", 
                # USAMOS self.fn_volver DIRECTAMENTE
                on_click=lambda _: lectura_ia.vista_lectura(self.page, self.fn_volver)
            )
        ], horizontal_alignment="center", spacing=20)