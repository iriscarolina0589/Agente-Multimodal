# Agente Multimodal

Este es el agente que he desarrollado para la práctica final de Inteligencia
Artificial. Analiza documentos académicos: le doy un artículo (en PDF, CSV, texto o
imagen) y, a partir de él, me genera un resumen, me extrae los metadatos, compara dos
trabajos y me deja hacerle preguntas sobre el contenido. Todo funciona en local, con
un modelo de lenguaje ejecutado mediante Ollama y orquestado con LangChain, sin
depender de servicios externos.

## Qué hace

- **Resumen** estructurado del artículo (resumen, objetivos, metodología, hallazgos y limitaciones).
- **Metadatos**: título, autores, año, publicación, palabras clave, datasets y métricas.
- **Comparativa** de dos artículos en una tabla.
- **Preguntas** de seguimiento sobre el documento, manteniendo el contexto de la conversación.

## Requisitos

- Python 3.11 o superior.
- Ollama instalado y en ejecución (https://ollama.com).

## Instalación

```bash
cd agente-multimodal

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

ollama pull llama3.1:8b
```

Hay que tener Ollama en marcha; su servidor escucha en `http://localhost:11434`.

## Cómo ejecutarlo

La forma más cómoda es la interfaz web:

```bash
streamlit run src/app.py
```

Se abre en el navegador (`http://localhost:8501`). Subo un documento en el panel de
la izquierda y uso las pestañas para resumir, ver los metadatos, comparar o preguntar.

También se puede usar desde la línea de comandos:

```bash
python src/cli.py resumir   ruta/a/tu_articulo.pdf
python src/cli.py comparar  articulo1.pdf articulo2.pdf
python src/cli.py chat      ruta/a/tu_articulo.pdf
```

## Configuración

Se puede ajustar con variables de entorno (todas tienen un valor por defecto):

| Variable | Por defecto | Para qué sirve |
| --- | --- | --- |
| `AGENTE_MODELO` | `llama3.1:8b` | Modelo de texto en Ollama. |
| `AGENTE_MODELO_VISION` | (vacío) | Modelo de visión para imágenes, p. ej. `llava:7b`. |
| `OLLAMA_HOST` | `http://localhost:11434` | Dirección del servidor de Ollama. |
| `AGENTE_TEMPERATURA` | `0.1` | Aleatoriedad de las respuestas. |
| `AGENTE_MAX_CHARS` | `12000` | Máximo de caracteres del documento que se envían al modelo. |

## Estructura

```
agente-multimodal/
  src/
    config.py          configuración (modelo, servidor, límites)
    prompts.py         un prompt para cada funcionalidad
    ingest.py          lectura de PDF, CSV, texto e imagen
    agent.py           orquestación con LangChain y salida estructurada
    app.py             interfaz web (Streamlit)
    cli.py             interfaz por línea de comandos
  memoria/             memoria técnica en PDF
  .streamlit/          configuración del tema de la interfaz
  requirements.txt     dependencias
```

La memoria técnica está en la carpeta `memoria/`
(`Memoria-Practica2-Iris-Fernandez.pdf`), con la explicación del dominio, la
arquitectura, las decisiones técnicas, los prompts y los ejemplos de uso.
