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

Es necesario tener Ollama en ejecución. El servidor corre en:
http://localhost:11434

## Cómo ejecutarlo

La forma más cómoda es la interfaz web:

```bash
streamlit run src/app.py
```

Se abre en el navegador (`http://localhost:8501`). Subo un documento en el panel de
la izquierda y uso las pestañas para resumir, ver los metadatos, comparar o preguntar.


## Configuración

El sistema funciona con valores por defecto, así que no es necesario configurar nada para probarlo.

Si quieres ajustarlo, puedes hacerlo mediante variables de entorno. Por ejemplo, puedes cambiar el modelo de lenguaje que se usa en Ollama, la dirección del servidor local, o algunos parámetros como la temperatura (que controla qué tan creativas o deterministas son las respuestas) y el tamaño máximo del texto que se envía al modelo.

Por defecto, el sistema usa el modelo llama3.1:8b en Ollama, conectado a http://localhost:11434. También trabaja con una temperatura baja para que las respuestas sean más estables y consistentes, y limita la cantidad de texto que procesa para evitar errores con documentos muy largos.

Si no modificas nada, todo funciona automáticamente con esos valores.


La memoria técnica está en la carpeta `memoria/`
(`Memoria-Practica2-Iris-Fernandez.pdf`), con la explicación del dominio, la
arquitectura, las decisiones técnicas, los prompts y los ejemplos de uso.
