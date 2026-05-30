"""Parametros de configuracion del agente.

Se leen de variables de entorno para poder cambiarlos sin tocar el codigo.
"""

import os

# Modelo de texto en Ollama. Llama 3.1 8B cuantizado cabe en una GPU de 8 GB.
MODELO_TEXTO = os.getenv("AGENTE_MODELO", "llama3.1:8b")

# Modelo de vision opcional para imagenes (por ejemplo "llava:7b").
MODELO_VISION = os.getenv("AGENTE_MODELO_VISION", "")

# Servidor local de Ollama.
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Temperatura baja: respuestas mas estables para resumir y extraer.
TEMPERATURA = float(os.getenv("AGENTE_TEMPERATURA", "0.1"))

# Limite de caracteres del documento que se envian al modelo.
MAX_CHARS_CONTEXTO = int(os.getenv("AGENTE_MAX_CHARS", "12000"))

# Ventana de contexto del modelo (tokens). Debe caber el documento recortado mas
# la respuesta; 8192 es suficiente para MAX_CHARS_CONTEXTO y cabe en una GPU de 8 GB.
NUM_CTX = int(os.getenv("AGENTE_NUM_CTX", "8192"))

# Cuanto mantiene Ollama el modelo cargado tras una peticion. Con 30m no se
# descarga de la GPU entre una consulta y otra durante una sesion de trabajo.
KEEP_ALIVE = os.getenv("AGENTE_KEEP_ALIVE", "30m")


def resumen_config():
    """Devuelve una linea con la configuracion activa, para mostrarla en la interfaz."""
    vision = MODELO_VISION or "(desactivado)"
    return f"modelo={MODELO_TEXTO} | vision={vision} | ollama={OLLAMA_BASE_URL}"
