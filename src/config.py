"""Configuración del agente.

Los valores se pueden cambiar desde variables de entorno sin tocar el código.
"""

import os

# Modelo principal que usa el agente en Ollama. Por defecto usa llama3.1:8b
MODELO_TEXTO = os.getenv("AGENTE_MODELO", "llama3.1:8b")

# Modelo opcional para imágenes (si se usa análisis visual)
MODELO_VISION = os.getenv("AGENTE_MODELO_VISION", "")

# Servidor local de Ollama.
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Controla qué tan creativas son las respuestas (bajo = más estable)
TEMPERATURA = float(os.getenv("AGENTE_TEMPERATURA", "0.1"))

# Límite aproximado del texto que se envía al modelo
MAX_CHARS_CONTEXTO = int(os.getenv("AGENTE_MAX_CHARS", "12000"))

# Tamaño de ventana de contexto del modelo (tokens)
NUM_CTX = int(os.getenv("AGENTE_NUM_CTX", "8192"))

# Mantiene el modelo cargado en memoria para evitar recargas constantes
KEEP_ALIVE = os.getenv("AGENTE_KEEP_ALIVE", "30m")


def resumen_config():
    """Devuelve un resumen rápido de la configuración activa."""
    vision = MODELO_VISION or "(desactivado)"
    return f"modelo={MODELO_TEXTO} | vision={vision} | ollama={OLLAMA_BASE_URL}"
