import os
import json
import glob
import subprocess
from pathlib import Path

# 1. Ruta por defecto donde Antigravity guarda las sesiones en Windows
RUTA_ANTIGRAVITY = Path(os.environ["USERPROFILE"]) / ".gemini" / "antigravity"

def extraer_tokens_locales():
    # Estructura inicial para contar tokens
    conteo_modelos = {
        "Gemini 3 Pro": 0,
        "Gemini 3 Flash": 0,
        "Otros Modelos": 0
    }
    
    # Buscamos en los archivos de almacenamiento de sesiones locales de la IDE
    archivos_sesion = glob.glob(str(RUTA_ANTIGRAVITY / "**" / "*.json*"), recursive=True)
    
    if not archivos_sesion:
        print("No se encontraron registros activos de Antigravity.")
        return conteo_modelos

    for ruta_archivo in archivos_sesion:
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                # Si el archivo está en formato JSONL (línea por línea)
                for linea in f:
                    if "token" in linea or "model" in linea:
                        datos = json.loads(linea.strip())
                        # Sumamos el total de tokens detectados por el uso del agente
                        modelo = datos.get("responseModel", "Otros Modelos")
                        tokens = datos.get("tokenCount", datos.get("input_tokens", 0))
                        
                        if "pro" in modelo.lower():
                            conteo_modelos["Gemini 3 Pro"] += tokens
                        elif "flash" in modelo.lower():
                            conteo_modelos["Gemini 3 Flash"] += tokens
                        else:
                            conteo_modelos["Otros Modelos"] += tokens
        except Exception:
            continue # Ignora archivos temporales bloqueados por la IDE
            
    return conteo_modelos

def subir_a_github():
    try:
        # Ejecuta comandos de Git para actualizar tu GitHub Pages de forma automatizada
        subprocess.run(["git", "add", "tokens.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Auto-update: Actualización de consumo de tokens"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("¡Web actualizada en GitHub Pages con éxito!")
    except subprocess.CalledProcessError as e:
        print(f"Error al subir a Git (Quizás no hay cambios nuevos): {e}")

if __name__ == "__main__":
    print("Extrayendo metadatos de tokens locales...")
    datos_actuales = extraer_tokens_locales()
    
    # Guardamos el JSON en la misma carpeta para que lo lea index.html
    with open("tokens.json", "w", encoding="utf-8") as archivo_json:
        json.dump(datos_actuales, archivo_json, indent=2)
        
    print("Subiendo datos actualizados a GitHub...")
    subir_a_github()
