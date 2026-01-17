import sqlite3
import pandas as pd
import os

DB_NAME = "vocabulario_aleman_niveles.db"
CSV_FILE = "vocabulario_niveles.csv" 

def init_db():
    if not os.path.exists(CSV_FILE):
        print(f"⚠️ ALERTA: No se encuentra {CSV_FILE}")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Crear tabla si no existe (Primera vez)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS palabras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aleman TEXT UNIQUE,
            espanol TEXT,
            nivel TEXT,
            aciertos INTEGER DEFAULT 0,
            medicina INTEGER DEFAULT 0 
        )
    ''')

    # 2. AUTO-REPARACIÓN: Chequear si falta la columna 'medicina' (Migración)
    cursor.execute("PRAGMA table_info(palabras)")
    columnas = [info[1] for info in cursor.fetchall()]
    
    if 'medicina' not in columnas:
        print("🔧 Actualizando base de datos antigua (Agregando sistema Hospital)...")
        try:
            cursor.execute("ALTER TABLE palabras ADD COLUMN medicina INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Base de datos actualizada con éxito.")
        except Exception as e:
            print(f"❌ Error actualizando DB: {e}")

    # 3. Cargar datos del CSV si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM palabras")
    if cursor.fetchone()[0] == 0:
        print("📥 Cargando datos desde CSV...")
        try:
            df = pd.read_csv(CSV_FILE)
            for _, row in df.iterrows():
                cursor.execute("INSERT OR IGNORE INTO palabras (aleman, espanol, nivel, aciertos, medicina) VALUES (?, ?, ?, 0, 0)", 
                               (row['aleman'], row['espanol'], row['nivel']))
            conn.commit()
            print("✅ Datos cargados.")
        except Exception as e:
            print(f"❌ Error leyendo CSV: {e}")
    
    conn.close()

# --- FUNCIONES NORMALES (MODO APRENDER) ---
def obtener_palabras_session(nivel, cantidad=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, aleman, espanol, nivel FROM palabras WHERE nivel = ? ORDER BY aciertos ASC, RANDOM() LIMIT ?", (nivel, cantidad))
    data = cursor.fetchall()
    conn.close()
    return data

# --- FUNCIONES HOSPITAL ---
def obtener_enfermas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Verifica que la columna exista antes de consultar (doble seguridad)
    try:
        cursor.execute("SELECT id, aleman, espanol, medicina FROM palabras WHERE medicina > 0 ORDER BY medicina DESC")
        data = cursor.fetchall()
    except sqlite3.OperationalError:
        return [] # Retorna vacío si hay error de DB
    conn.close()
    return data

def actualizar_progreso(id_palabra, resultado, modo="normal"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if resultado == "bien":
        if modo == "hospital":
            cursor.execute("UPDATE palabras SET medicina = medicina - 1 WHERE id = ?", (id_palabra,))
            cursor.execute("UPDATE palabras SET medicina = 0 WHERE medicina < 0 AND id = ?", (id_palabra,))
        else:
            cursor.execute("UPDATE palabras SET aciertos = aciertos + 1 WHERE id = ?", (id_palabra,))
    else: 
        # Fallo: Castigo + Reset
        cursor.execute("UPDATE palabras SET medicina = 3, aciertos = 0 WHERE id = ?", (id_palabra,))
        
    conn.commit()
    conn.close()

# --- FUNCIONES BLITZ ---
def obtener_palabras_blitz(cantidad=50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, aleman, espanol, nivel FROM palabras ORDER BY RANDOM() LIMIT ?", (cantidad,))
    data = cursor.fetchall()
    conn.close()
    return data

def obtener_estadisticas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    niveles = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    stats = {}
    
    for nv in niveles:
        cursor.execute("SELECT COUNT(*) FROM palabras WHERE nivel = ?", (nv,))
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM palabras WHERE nivel = ? AND aciertos > 0", (nv,))
        aprendidas = cursor.fetchone()[0]
        
        if total > 0:
            stats[nv] = aprendidas / total
            stats[f"{nv}_txt"] = f"{aprendidas}/{total}"
        else:
            stats[nv] = 0
            stats[f"{nv}_txt"] = "0/0"
    
    # Stats Hospital (Protegido contra errores)
    try:
        cursor.execute("SELECT COUNT(*) FROM palabras WHERE medicina > 0")
        enfermas = cursor.fetchone()[0]
    except:
        enfermas = 0
        
    stats["hospital_count"] = enfermas
    conn.close()
    return stats

init_db()