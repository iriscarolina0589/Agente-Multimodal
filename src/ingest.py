"""Lectura de documentos: convierte PDF, CSV, texto o imagen a texto plano."""

import base64
from pathlib import Path

import config

EXT_PDF = {".pdf"}
EXT_CSV = {".csv"}
EXT_TXT = {".txt", ".md"}
EXT_IMG = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def cargar_pdf(ruta):
    """Extrae el texto de un PDF con PyMuPDF."""
    import fitz

    with fitz.open(ruta) as doc:
        return "\n".join(pagina.get_text() for pagina in doc).strip()


def cargar_csv(ruta):
    """Lee un CSV y lo resume en texto (cabecera, primeras filas y estadisticos)."""
    import pandas as pd

    def a_texto(frame):
        # to_markdown necesita tabulate; si no esta, usamos to_string.
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
    """Lee un archivo de texto plano."""
    return Path(ruta).read_text(encoding="utf-8", errors="ignore").strip()


def cargar_imagen(ruta):
    """Transcribe una imagen a texto con un modelo de vision de Ollama.

    Requiere configurar AGENTE_MODELO_VISION; si no, avisa en lugar de fallar.
    """
    if not config.MODELO_VISION:
        raise ValueError("Configura un modelo de vision en AGENTE_MODELO_VISION "
                         "(por ejemplo 'llava:7b') para procesar imagenes.")
    from langchain_core.messages import HumanMessage
    from langchain_ollama import ChatOllama
    from prompts import PROMPT_VISION

    datos = base64.b64encode(Path(ruta).read_bytes()).decode("utf-8")
    llm = ChatOllama(model=config.MODELO_VISION, base_url=config.OLLAMA_BASE_URL, temperature=0)
    mensaje = HumanMessage(content=[
        {"type": "text", "text": PROMPT_VISION},
        {"type": "image_url", "image_url": f"data:image/png;base64,{datos}"},
    ])
    return llm.invoke([mensaje]).content.strip()


def cargar_documento(ruta):
    """Detecta el tipo de archivo por su extension y devuelve su texto.

    El resultado se recorta a MAX_CHARS_CONTEXTO para no pasarse de la ventana
    de contexto del modelo.
    """
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

    if len(texto) > config.MAX_CHARS_CONTEXTO:
        texto = texto[:config.MAX_CHARS_CONTEXTO] + "\n[...documento recortado...]"
    return texto
