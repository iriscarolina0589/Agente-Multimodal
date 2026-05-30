"""Prompts del agente.

Cada funcionalidad del sistema tiene su propio prompt (resumen, metadatos,
comparacion y preguntas) para mejorar la precision.

Todos parten de una misma base que define el estilo de respuesta y evita
que el modelo invente informacion que no esta en el documento.
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Instruccion base que comparten todos los prompts
# Define el tono, idioma y regla principal: no inventar informacion
ROL_BASE = (
    "Eres un asistente experto en analizar articulos cientificos. Respondes siempre "
    "en espanol, de forma clara y estructurada. Te basas solo en el contenido del "
    "documento; si algo no aparece, indica 'No consta en el documento' en lugar de "
    "inventarlo."
)

# Prompt para generar el resumen general del documento
PROMPT_RESUMEN = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Escribe un resumen general del articulo en 2 o 3 frases."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\nEscribe el resumen general.'),
])

# Prompt para extraer las secciones del resumen por separado
# Esto ayuda a que el modelo no mezcle todo en un unico texto
PROMPT_SECCIONES = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae del documento los objetivos, la metodologia, los "
               "hallazgos clave y las limitaciones. Rellena los CUATRO campos con "
               "informacion del documento; no dejes ninguno vacio."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\n'
              "Indica los objetivos, la metodologia, los hallazgos y las limitaciones."),
])

# Prompt para obtener metadatos bibliograficos del documento
PROMPT_ENTIDADES = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae los metadatos del documento: titulo, autores, "
               "ano, publicacion, palabras clave, datasets y metricas."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\nExtrae los metadatos.'),
])

# Prompt para crear una ficha resumida del documento (usada en comparaciones)
PROMPT_FICHA = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Extrae cuatro datos del documento: el objetivo, el metodo, "
               "los datos o dataset usados y los resultados. Rellena los CUATRO campos "
               "con informacion del documento; no dejes ninguno vacio."),
    ("human", 'Documento:\n"""\n{documento}\n"""\n\n'
              "Resume en una o dos frases el objetivo, el metodo, los datos y los resultados."),
])

# Prompt para generar la conclusion al comparar dos documentos
PROMPT_CONCLUSION = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Resume en una o dos frases la diferencia clave entre los "
               "dos trabajos e indica para que es mejor cada uno."),
    ("human",
     "Documento A -> objetivo: {obj_a}; metodo: {met_a}; datos: {dat_a}; resultados: {res_a}\n"
     "Documento B -> objetivo: {obj_b}; metodo: {met_b}; datos: {dat_b}; resultados: {res_b}\n\n"
     "Escribe la conclusion comparativa."),
])

# # Prompt para preguntas sobre el documento con contexto de conversacion
PROMPT_QA = ChatPromptTemplate.from_messages([
    ("system", ROL_BASE + " Responde a las preguntas sobre el documento teniendo en "
               "cuenta la conversacion previa, para resolver referencias como "
               "'ese estudio' o 'el anterior'."),
    ("system", 'Documento:\n"""\n{documento}\n"""'),
    MessagesPlaceholder("historial"),
    ("human", "{pregunta}"),
])

# Prompt para vision (imagenes o paginas escaneadas)
PROMPT_VISION = (
    "Transcribe el texto visible de esta imagen (pagina o figura de un documento "
    "academico). Describe brevemente tablas o graficos si los hay. Responde en "
    "espanol y no inventes texto."
)
