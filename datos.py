import sqlite3
import random
import csv
import os

# Nombre del archivo CSV que bajaste de Colab
ARCHIVO_CSV = "vocabulario_aleman_500.csv"
DB_NAME = "vocabulario_aleman_500db"

def crear_base_datos():
    # Solo creamos la DB si no existe el archivo .db o está vacío
    reconstruir = False
    if not os.path.exists(DB_NAME):
        reconstruir = True
        
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palabras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aleman TEXT,
            espanol TEXT
        )
    """)
    
    cursor.execute("SELECT count(*) FROM palabras")
    cantidad = cursor.fetchone()[0]
    
    # Si la tabla está vacía y tenemos un CSV, cargamos los datos
    if cantidad == 0 and os.path.exists(ARCHIVO_CSV):
        print("Cargando datos desde CSV...")
        try:
            with open(ARCHIVO_CSV, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader) # Saltamos la cabecera (títulos de columnas)
                
                # Leemos todo el CSV y lo metemos a la DB
                lista_datos = []
                for row in reader:
                    if len(row) >= 2: # Asegurar que tenga aleman y espanol
                        lista_datos.append((row[0], row[1]))
                
                cursor.executemany("INSERT INTO palabras (aleman, espanol) VALUES (?, ?)", lista_datos)
                conexion.commit()
                print(f"¡Éxito! Se cargaron {len(lista_datos)} palabras del CSV.")
        except Exception as e:
            print(f"Error leyendo el CSV: {e}")
            # FALLBACK: Si falla el CSV, usamos una lista de emergencia pequeña
            lista_emergencia = [("Der Fehler", "El Error"), ("Das Problem", "El Problema")]
            cursor.executemany("INSERT INTO palabras (aleman, espanol) VALUES (?, ?)", lista_emergencia)
            conexion.commit()
            
    conexion.close()

def obtener_palabra_random():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("SELECT aleman, espanol FROM palabras")
    todas = cursor.fetchall()
    conexion.close()
    if todas:
        return random.choice(todas)
    return ("No Data", "Verifica el CSV")

def obtener_todas():
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("SELECT id, aleman, espanol FROM palabras")
    todas = cursor.fetchall()
    conexion.close()
    return todas

def agregar_palabra(aleman, espanol):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO palabras (aleman, espanol) VALUES (?, ?)", (aleman, espanol))
    conexion.commit()
    conexion.close()

def borrar_palabra(id_palabra):
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM palabras WHERE id = ?", (id_palabra,))
    conexion.commit()
    conexion.close()


def existe_palabra(palabra_aleman):
    """
    Devuelve True si la palabra ya existe en la base de datos,
    False si es nueva.
    """
    conexion = sqlite3.connect(DB_NAME) # Asegúrate que DB_NAME sea el correcto, o usa "vocabulario.db"
    cursor = conexion.cursor()
    
    # Buscamos la palabra ignorando mayúsculas/minúsculas (NOCASE)
    cursor.execute("SELECT id FROM palabras WHERE aleman = ? COLLATE NOCASE", (palabra_aleman.strip(),))
    resultado = cursor.fetchone()
    
    conexion.close()
    
    # Si hay resultado, es True (existe). Si es None, es False (no existe).
    return resultado is not None

# Inicializar al importar
crear_base_datos()