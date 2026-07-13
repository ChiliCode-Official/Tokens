import os
import json
import glob
import subprocess
from pathlib import Path

# Ruta oficial de logs de caché donde Google Antigravity guarda la telemetría en Windows
RUTA_ANTIGRAVITY = Path(os.environ["USERPROFILE"]) / ".gemini" / "antigravity" / ".token-monitor" / "rpc-cache" / "v1"

def extraer_tokens_locales():
    # Estructura inicial para el conteo de tokens
    conteo_modelos = {
        "Gemini Models": 0,
        "Claude Models": 0,
        "Otros Modelos": 0
    }
    
    # Buscamos archivos JSONL o JSON dentro del rpc-cache de Antigravity
    archivos_sesion = glob.glob(str(RUTA_ANTIGRAVITY / "**" / "*.json*"), recursive=True)
    
    if not archivos_sesion:
        print("No se encontraron registros activos en la ruta de telemetría de Antigravity.")
        print(f"Ruta buscada: {RUTA_ANTIGRAVITY}")
        return conteo_modelos

    for ruta_archivo in archivos_sesion:
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    linea_limpia = linea.strip()
                    if not linea_limpia:
                        continue
                    
                    try:
                        datos = json.loads(linea_limpia)
                    except json.JSONDecodeError:
                        continue # Salta líneas corruptas o fragmentadas
                    
                    # Buscamos claves de conteo de tokens (tokenCount, input_tokens, usage, etc.)
                    # El formato de Antigravity varía si es un snapshot o un volcado de trayectoria
                    modelo = datos.get("responseModel", datos.get("model", "Otros Modelos")).lower()
                    
                    # Extraer conteo de tokens
                    tokens = 0
                    if "tokenCount" in datos:
                        tokens = datos["tokenCount"]
                    elif "usage" in datos and isinstance(datos["usage"], dict):
                        tokens = datos["usage"].get("total_tokens", datos["usage"].get("input_tokens", 0))
                    elif "input_tokens" in datos:
                        tokens = datos["input_tokens"] + datos.get("output_tokens", 0)

                    # Clasificación según el ecosistema del modelo asignado por la IDE
                    if "gemini" in modelo:
                        conteo_modelos["Gemini Models"] += tokens
                    elif "claude" in modelo or "sonnet" in modelo or "opus" in modelo:
                        conteo_modelos["Claude Models"] += tokens
                    else:
                        # Si tiene tokens pero no coincide el nombre exacto, lo agrupa en otros
                        if tokens > 0:
                            conteo_modelos["Otros Modelos"] += tokens
        except Exception as e:
            continue # Ignorar si la IDE tiene bloqueado temporalmente el archivo de sesión
            
    return conteo_modelos

def subir_a_github():
    try:
        print("Sincronizando archivos con el repositorio Git...")
        # Forzar la adición de los dos archivos esenciales
        subprocess.run(["git", "add", "tokens.json", "index.html"], check=True, shell=True)
        
        # Ejecuta el commit con una marca de tiempo automática
        subprocess.run(["git", "commit", "-m", "Auto-update: Actualización de telemetría desde Antigravity IDE"], check=True, shell=True)
        
        # Sube los cambios a la rama principal (main o master)
        subprocess.run(["git", "push", "origin", "main"], check=True, shell=True)
        print("¡Éxito! Tu sitio en GitHub Pages ya refleja tus consumos actualizados.")
    except subprocess.CalledProcessError as e:
        print("\n[Aviso] No se detectaron cambios nuevos para hacer push o Git no está listo.")
        print("Asegúrate de que estás en la carpeta correcta y de haber corrido 'git init'.")

if __name__ == "__main__":
    print("Iniciando extracción de metadatos de Google Antigravity...")
    datos_actuales = extraer_tokens_locales()
    
    # Imprime en la consola local un resumen para verificar que funciona
    print("\nResumen obtenido:")
    for mod, tok in datos_actuales.items():
        print(f" - {mod}: {tok:,} tokens")
        
    # Guarda/reemplaza el archivo local tokens.json para el index.html
    with open("tokens.json", "w", encoding="utf-8") as archivo_json:
        json.dump(datos_actuales, archivo_json, indent=2)
        
    # Dispara la subida automática a GitHub Pages
    subir_a_github()
