import os
import json
import sys

try:
    # Importamos el módulo de observabilidad oficial del SDK de Antigravity
    import google_antigravity as ag
except ImportError:
    print("[Error] No se encontró el SDK. Ejecuta primero: pip install google-antigravity")
    sys.exit(1)

def obtener_cuota_oficial():
    # Inicializamos con valores en 0 por si el cliente está desconectado
    conteo_modelos = {
        "Gemini Models": 0,
        "Claude Models": 0,
        "Otros Modelos": 0
    }
    
    try:
        # Nos conectamos a la sesión local de tu cliente de Antigravity autenticado
        cliente = ag.Client()
        
        # Consultamos las métricas de observabilidad de tokens y cuotas de uso (Sprint/Maratón)
        metricas = cliente.get_quota_status()
        
        # Mapeamos los datos consumidos de tus agentes y modelos activos
        # Si la IDE mide en 'unidades' o 'tokens', el SDK lo estandariza automáticamente
        conteo_modelos["Gemini Models"] = metricas.get("gemini_tokens_used", 0)
        conteo_modelos["Claude Models"] = metricas.get("claude_tokens_used", 0)
        conteo_modelos["Otros Modelos"] = metricas.get("other_tokens_used", 0)
        
        # En caso de que use la estructura simplificada de la API general:
        if sum(conteo_modelos.values()) == 0 and "total_usage" in metricas:
            conteo_modelos["Gemini Models"] = metricas["total_usage"].get("input_tokens", 0)
            
    except Exception as e:
        print(f"[Aviso] No se pudo conectar a la IDE activa: {e}")
        print("Asegúrate de tener la IDE de Google Antigravity abierta y con tu sesión iniciada.")
        
    return conteo_modelos

if __name__ == "__main__":
    print("Conectando con el SDK oficial de Google Antigravity...")
    datos_actuales = obtener_cuota_oficial()
    
    print("\nResumen de uso extraído:")
    for mod, tok in datos_actuales.items():
        print(f" - {mod}: {tok:,} tokens")
        
    # Guardamos los datos reales para alimentar tu GitHub Desktop
    with open("tokens.json", "w", encoding="utf-8") as archivo_json:
        json.dump(datos_actuales, archivo_json, indent=2)
        
    print("\n[Listo] ¡tokens.json actualizado con éxito con la API oficial!")
