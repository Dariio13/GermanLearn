import cerebro
import datos
import time

# --- TEMARIO MASIVO (A1, A2, B1, B2) ---
temario = [
    # === NIVEL A1 (Principiante) ===
    ("A1", "Mi familia y yo (Meine Familie)"),
    ("A1", "Presentación personal"),
    ("A1", "En el supermercado (Comida)"),
    ("A1", "Mis hobbies y tiempo libre"),
    ("A1", "Los colores y la ropa"),
    ("A1", "Mi apartamento y los muebles"),
    ("A1", "El clima y las estaciones"),
    ("A1", "En la estación de tren"),
    ("A1", "Cita con el médico"),
    ("A1", "Pedir en el restaurante"),
    ("A1", "Los días de la semana y la hora"),
    ("A1", "Animales domésticos"),
    ("A1", "Mi ciudad favorita"),
    ("A1", "Cumpleaños y regalos"),
    ("A1", "En la escuela de idiomas"),

    # === NIVEL A2 (Básico Alto) ===
    ("A2", "Mis últimas vacaciones (Pasado)"),
    ("A2", "Buscando trabajo (Profesiones)"),
    ("A2", "Mi rutina diaria"),
    ("A2", "Invitación a una fiesta"),
    ("A2", "Problemas con el coche"),
    ("A2", "En el hotel (Recepción)"),
    ("A2", "Describir personas (Físico y carácter)"),
    ("A2", "Medios de transporte y tráfico"),
    ("A2", "Planes para el futuro (Futuro)"),
    ("A2", "Escribir un email formal"),
    ("A2", "En la farmacia"),
    ("A2", "Buscando piso (Alquiler)"),
    ("A2", "Deportes y salud"),
    ("A2", "Instrucciones de cocina"),
    ("A2", "Ver la televisión y noticias"),

    # === NIVEL B1 (Intermedio) ===
    ("B1", "Entrevista de trabajo detallada"),
    ("B1", "El medio ambiente y reciclaje"),
    ("B1", "La vida sin internet"),
    ("B1", "Historia de Berlín (Muro)"),
    ("B1", "Ventajas de vivir en el campo"),
    ("B1", "Sistema educativo en Alemania"),
    ("B1", "Conflictos vecinales"),
    ("B1", "Costumbres culturales alemanas"),
    ("B1", "Quejarse por un producto defectuoso"),
    ("B1", "Amistad y relaciones"),
    ("B1", "Viajes de negocios"),
    ("B1", "Festivales de música"),

    # === NIVEL B2 (Avanzado) ===
    ("B2", "El cambio climático global"),
    ("B2", "Política y elecciones"),
    ("B2", "Inteligencia Artificial en el futuro"),
    ("B2", "El equilibrio vida-trabajo (Work-Life-Balance)"),
    ("B2", "Literatura alemana clásica"),
    ("B2", "La economía europea"),
    ("B2", "Inmigración e integración"),
    ("B2", "Debate sobre energías renovables"),
    ("B2", "Psicología y estrés moderno"),
    ("B2", "Arte moderno y museos")
]

def llenar_base_de_datos():
    print("🚀 INICIANDO GENERACIÓN MASIVA...")
    datos.init_db() 
    
    total = len(temario)
    for i, (nivel, tema) in enumerate(temario):
        print(f"[{i+1}/{total}] 🤖 Generando ({nivel}): {tema}...")
        
        # Verificamos si ya existe para no gastar doble (opcional, pero útil)
        # Por simplicidad, aquí sobrescribimos o agregamos.
        
        contenido = cerebro.generar_leccion_historia(nivel, tema)
        
        if contenido:
            datos.guardar_leccion(nivel, tema, contenido)
            print(f"   ✅ Guardado: {contenido['titulo']}")
        else:
            print("   ❌ Falló.")
            
        time.sleep(1) # Respetamos a la API

    print("\n🎉 ¡BIBLIOTECA COMPLETADA!")

if __name__ == "__main__":
    llenar_base_de_datos()