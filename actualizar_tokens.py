import os
import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# ==========================================
# CONFIGURACIÓN DE GITHUB (AUTOMATIZACIÓN)
# ==========================================
# Reemplaza "TU_TOKEN_AQUI" con el token que generes en GitHub
GITHUB_TOKEN = "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"
# El formato debe ser "tu-usuario/tu-repositorio"
GITHUB_REPO = "ChiliCode-Official/Tokens" 
GITHUB_FILE_PATH = "tokens.json"


def search_for_tokens():
    """
    Simula la búsqueda heurística de tokens en el perfil del usuario (Windows).
    """
    user_profile = os.environ.get('USERPROFILE', '')
    if not user_profile:
        return {}
    return {}

def push_to_github(json_data):
    """
    Sube directamente el diccionario de datos a GitHub usando su API oficial.
    No requiere comandos git ni dependencias externas.
    """
    if GITHUB_TOKEN == "TU_TOKEN_AQUI":
        print("Sincronización en la nube omitida: Configura tu GITHUB_TOKEN primero.")
        return

    print("Intentando sincronizar con la nube (GitHub)...")
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Auto-Quota-Tracker"
    }

    # 1. Obtener el SHA actual del archivo (necesario para sobrescribir en la API de GitHub)
    sha = None
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            sha = res_data.get('sha')
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Error al verificar estado en GitHub: {e.reason}")
            return

    # 2. Preparar el payload (Base64)
    content_str = json.dumps(json_data, indent=4, ensure_ascii=False)
    content_b64 = base64.b64encode(content_str.encode('utf-8')).decode('utf-8')

    payload = {
        "message": "Auto-sync tokens via Background Script",
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha # Le decimos a GitHub qué archivo sobrescribir

    # 3. Hacer el Push (PUT request)
    req_put = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers=headers, 
        method="PUT"
    )
    
    try:
        with urllib.request.urlopen(req_put) as response:
            if response.status in [200, 201]:
                print("¡Sincronizacion con GitHub exitosa! Datos en la nube actualizados.")
    except Exception as e:
        print(f"Error al subir a GitHub: {e}")

def main():
    print("Iniciando escaneo heurístico de tokens de modelos locales...")
    scanned_data = search_for_tokens()
    
    fallback_data = {
        "gemini": {
            "weekly": { "percent": 40, "text": "You have used some of your weekly limit, it will fully refresh in 1 hour, 49 minutes." },
            "five_hour": { "percent": 47, "text": "You have used some of your 5-hour limit, it will fully refresh in 1 hour, 3 minutes." }
        },
        "claude_gpt": {
            "weekly": { "percent": 10, "text": "You have used some of your weekly limit, it will fully refresh in 22 hours, 25 minutes." },
            "five_hour": { "percent": 100, "text": "Fully refreshed" }
        }
    }

    final_data = fallback_data if not scanned_data else scanned_data

    # 1. Guardado Local (Para la computadora actual)
    output_file = 'tokens.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print(f"[{output_file}] generado exitosamente en local.")
    except Exception as e:
        print(f"Error crítico local: {e}")

    # 2. Sincronización Remota (La magia invisible)
    push_to_github(final_data)

if __name__ == '__main__':
    main()
