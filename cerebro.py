import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODELO = "gpt-4o-mini"

def generar_leccion_historia(nivel, tema):
    """
    Genera historia, traducción, gramática Y AHORA UN QUIZ.
    """
    prompt = f"""
    Eres un profesor de alemán experto. Crea una lección educativa de nivel {nivel} sobre: "{tema}".
    
    Respuesta OBLIGATORIA en JSON con esta estructura exacta:
    {{
        "titulo": "Título en Alemán (y español entre paréntesis)",
        "historia": "Historia en alemán (aprox 80-100 palabras) adaptada al nivel.",
        "traduccion": "Traducción al español.",
        "punto_gramatical": "Nombre de la regla clave.",
        "explicacion_gramatica": "Explicación breve en español.",
        "vocabulario_clave": ["Palabra1 (Significado)", "Palabra2 (Significado)"],
        "quiz": [
            {{
                "pregunta": "¿Pregunta sobre el texto en español?",
                "opciones": ["Opción A", "Opción B", "Opción C"],
                "respuesta_correcta": 0 
            }},
            {{
                "pregunta": "¿Segunda pregunta...",
                "opciones": ["...", "...", "..."],
                "respuesta_correcta": 1
            }},
            {{
                "pregunta": "¿Tercera pregunta...",
                "opciones": ["...", "...", "..."],
                "respuesta_correcta": 2
            }}
        ]
    }}
    NOTA: 'respuesta_correcta' es el índice de la opción correcta (0, 1 o 2).
    """

    try:
        response = client.chat.completions.create(
            model=MODELO,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ Error OpenAI: {e}")
        return None