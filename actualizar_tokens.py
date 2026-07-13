import os
import json
import glob
from pathlib import Path

# Buscaremos de forma más amplia dentro de la carpeta principal de la IDE
RUTA_RAIZ_ANTIGRAVITY = Path(os.environ["USERPROFILE"]) / ".gemini" / "antigravity"

def extraer_tokens_locales():
    conteo_modelos = {
        "Gemini Models": 0,
        "Claude Models": 0,
        "Otros Modelos": 0
    }
    
    # Buscamos absolutamente cualquier archivo JSON en toda la carpeta de Antigravity
    # Esto asegura capturar los registros sin importar la subcarpeta exacta de la versión
    archivos_sesion = glob.glob(str(RUTA_RAIZ_ANTIGRAVITY / "**" / "*.json*"), recursive=True)
    
    if not archivos_sesion:
        print("No se encontraron archivos de configuración o registros.")
        print(f"Ruta raíz revisada: {RUTA_RAIZ_ANTIGRAVITY}")
        return conteo_modelos

    for ruta_archivo in archivos_sesion:
        # Ignoramos archivos de configuración del sistema para no perder tiempo
        if "config" in ruta_archivo.lower() or "settings" in ruta_archivo.lower():
            continue
            
        try:
            with open(ruta_archivo, 'r', encoding='utf-8', errors='ignore') as f:
                for linea in f:
                    linea_limpia = linea.strip()
                    if not linea_limpia or not (linea_limpia.startswith('{') or '"' in linea_limpia):
                        continue
                    
                    try:
                        datos = json.loads(linea_limpia)
                    except json.JSONDecodeError:
                        continue
                    
                    # Extraer modelo
                    modelo = datos.get("responseModel", datos.get("model", datos.get("model_name", "Otros Modelos"))).lower()
                    
                    # Extraer tokens mediante diferentes variantes de nombres de variables de la IDE
                    tokens = 0
                    if "tokenCount" in datos:
                        tokens = datos["tokenCount"]
                    elif "usage" in datos and isinstance(datos["usage"], dict):
                        tokens = datos["usage"].get("total_tokens", datos["usage"].get("input_tokens", 0))
                    elif "input_tokens" in datos:
                        tokens = datos["input_tokens"] + datos.get("output_tokens", 0)
                    elif "tokens" in datos:
                        tokens = datos["tokens"]

                    if tokens > 0:
                        if "gemini" in modelo:
                            conteo_modelos["Gemini Models"] += tokens
                        elif "claude" in modelo or "sonnet" in modelo or "opus" in modelo:
                            conteo_modelos["Claude Models"] += tokens
                        else:
                            conteo_modelos["Otros Modelos"] += tokens
        except Exception:
            continue
            
    return conteo_modelos

if __name__ == "__main__":
    print("Iniciando extracción profunda en Google Antigravity...")
    datos_actuales = extraer_tokens_locales()
    
    print("\nResumen obtenido con éxito:")
    for mod, tok in datos_actuales.items():
        print(f" - {mod}: {tok:,} tokens")
        
    # Guardamos el archivo tokens.json local para que lo use tu GitHub Desktop
    with open("tokens.json", "w", encoding="utf-8") as archivo_json:
        json.dump(datos_actuales, archivo_json, indent=2)
    print("\n[Listo] Archivo tokens.json actualizado. Abre GitHub Desktop para subirlo.")
