"""Lectura de documentos y conversión a texto plano"""

import base64
from pathlib import Path

import config
# Tipos de archivo que puede procesar el sistema
EXT_PDF = {".pdf"}
EXT_CSV = {".csv"}
EXT_TXT = {".txt", ".md"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def cargar_pdf(ruta):
    """Extrae texto de un PDF."""
    import fitz

    with fitz.open(ruta) as doc:
        return "\n".join(pagina.get_text() for pagina in doc).strip()


def cargar_csv(ruta):
    """Convierte un CSV en texto resumido para el modelo."""
    import pandas as pd

    def a_texto(frame):
        # convierte el dataframe a texto legible
        try:
            return frame.to_markdown(index=False)
        except ImportError:
            return frame.to_string(index=False)

    df = pd.read_csv(ruta)
    try:
        stats = a_texto(df.describe(include="all"))
    except Exception:
        stats = "(sin estadisticos)"
    return (f"CSV con {len(df)} filas y {len(df.columns)} columnas.\n"
            f"Columnas: {', '.join(map(str, df.columns))}\n\n"
            f"Primeras filas:\n{a_texto(df.head(20))}\n\nEstadisticos:\n{stats}")


def cargar_texto(ruta):
    """Lee archivos de texto plano."""
    return Path(ruta).read_text(encoding="utf-8", errors="ignore").strip()


def cargar_imagen(ruta):
    """Convierte una imagen a texto usando un modelo de visión."""
    if not config.MODELO_VISION:
        raise ValueError("Configura un modelo de vision en AGENTE_MODELO_VISION "
                         "(por ejemplo 'llava:7b') para procesar imagenes.")
    from langchain_core.messages import HumanMessage
    from langchain_ollama import ChatOllama
    from prompts import PROMPT_VISION
    # prepara la imagen en base64 para enviarla al modelo
    datos = base64.b64encode(Path(ruta).read_bytes()).decode("utf-8")
    llm = ChatOllama(model=config.MODELO_VISION, base_url=config.OLLAMA_BASE_URL, temperature=0)
    mensaje = HumanMessage(content=[
        {"type": "text", "text": PROMPT_VISION},
        {"type": "image_url", "image_url": f"data:image/png;base64,{datos}"},
    ])
    return llm.invoke([mensaje]).content.strip()


def cargar_documento(ruta):
    """Detecta el tipo de archivo y lo convierte a texto."""
    ext = Path(ruta).suffix.lower()
    if ext in EXT_PDF:
        texto = cargar_pdf(ruta)
    elif ext in EXT_CSV:
        texto = cargar_csv(ruta)
    elif ext in EXT_TXT:
        texto = cargar_texto(ruta)
    elif ext in EXT_IMG:
        texto = cargar_imagen(ruta)
    else:
        raise ValueError(f"Tipo de archivo no soportado: {ext}")
    # recorta el texto si es demasiado largo para el modelo
    if len(texto) > config.MAX_CHARS_CONTEXTO:
        texto = texto[:config.MAX_CHARS_CONTEXTO] + "\n[...documento recortado...]"
    return texto
