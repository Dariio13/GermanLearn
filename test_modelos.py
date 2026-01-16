from google import genai

# 1. Pon tu clave aquí
client = genai.Client(api_key="AIzaSyDn3w8DN54_w_0nzc_Wyc9ns_6wKfFGUM4")

print("--- BUSCANDO MODELOS DISPONIBLES ---")

try:
    # Pedimos la lista a Google
    for model in client.models.list():
        # Filtramos solo los que sirven para generar contenido (texto/imagen)
        if "generateContent" in model.supported_actions:
            # Imprimimos el nombre exacto que debes usar
            print(f"Nombre válido: {model.name}")
            # Le quitamos el prefijo 'models/' para dártelo limpio
            clean_name = model.name.replace("models/", "")
            print(f"👉 Copia y usa este: {clean_name}")
            print("-" * 20)

except Exception as e:
    print(f"Error: {e}")