"""Prompts del agente.

Hay un prompt distinto para cada funcionalidad (resumen, metadatos, comparacion y
preguntas), en vez de uno generico. Todos comparten un rol base que fija el idioma
y pide no inventar informacion que no este en el documento.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

ROL_BASE = (
    "Eres un asistente experto en analizar articulos cientificos. Respondes siempre "
    "en espanol, de forma clara y estructurada. Te basas solo en el contenido del "
    "documento; si algo no aparece, indica 'No consta en el documento' en lugar de "
    "inventarlo."
)

# Resumen general (parrafo) del articulo.
PROMPT_RESUMEN = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Escribe un resumen general del articulo en 2 o 3 frases."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\nEscribe el resumen general.'),
])

# Secciones del resumen. Se extraen aparte (sin el campo 'resumen') para que el
# modelo pequeno rellene cada una en vez de volcarlo todo en el resumen general.
PROMPT_SECCIONES = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae del documento los objetivos, la metodologia, los "
               "hallazgos clave y las limitaciones. Rellena los CUATRO campos con "
               "informacion del documento; no dejes ninguno vacio."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\n'
              "Indica los objetivos, la metodologia, los hallazgos y las limitaciones."),
])

# Metadatos bibliograficos.
PROMPT_ENTIDADES = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae los metadatos del documento: titulo, autores, "
               "ano, publicacion, palabras clave, datasets y metricas."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\nExtrae los metadatos.'),
])

# Ficha de un documento (se usa para construir la comparacion).
PROMPT_FICHA = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae cuatro datos del documento: el objetivo, el metodo, "
               "los datos o dataset usados y los resultados. Rellena los CUATRO campos "
               "con informacion del documento; no dejes ninguno vacio."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\n'
              "Resume en una o dos frases el objetivo, el metodo, los datos y los resultados."),
])

# Conclusion de la comparacion a partir de las dos fichas.
PROMPT_CONCLUSION = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Resume en una o dos frases la diferencia clave entre los "
               "dos trabajos e indica para que es mejor cada uno."),
    ("human",
     "Documento A -> objetivo: {obj_a}; metodo: {met_a}; datos: {dat_a}; resultados: {res_a}\n"
     "Documento B -> objetivo: {obj_b}; metodo: {met_b}; datos: {dat_b}; resultados: {res_b}\n\n"
     "Escribe la conclusion comparativa."),
])

# Preguntas de seguimiento; incluye el historial para mantener el contexto.
PROMPT_QA = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Responde a las preguntas sobre el documento teniendo en "
               "cuenta la conversacion previa, para resolver referencias como "
               "'ese estudio' o 'el anterior'."),
    ("system", 'Documento:\n"""\n{documento}\n"""'),
    MessagesPlaceholder("historial"),
    ("human", "{pregunta}"),
])

# Transcripcion de imagenes con un modelo de vision (ruta opcional).
PROMPT_VISION = (
    "Transcribe el texto visible de esta imagen (pagina o figura de un documento "
    "academico). Describe brevemente tablas o graficos si los hay. Responde en "
    "espanol y no inventes texto."
)
