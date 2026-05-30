"""Agente de analisis de documentos academicos.

Orquesta con LangChain el modelo local de Ollama: chains por funcionalidad, salida
estructurada con Pydantic, memoria de conversacion y un agente con herramientas.
"""

from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_ollama import ChatOllama

import config
import ingest
import prompts


# Esquemas de salida estructurada.
class ResumenArticulo(BaseModel):
    """Lo que quiero que el modelo saque al resumir un articulo."""
    resumen: str = Field(description="Resumen general del articulo en 2 o 3 frases.")
    objetivos: list[str] = Field(
        default_factory=list,
        description="Objetivos o metas del estudio, como lista de frases breves.")
    metodologia: str = Field(
        default="", description="Metodologia, tecnicas o enfoque que emplea el estudio.")
    hallazgos: list[str] = Field(
        default_factory=list,
        description="Hallazgos o resultados principales, como lista de frases breves.")
    limitaciones: list[str] = Field(
        default_factory=list,
        description="Limitaciones del estudio o del trabajo, como lista de frases breves.")


class SeccionesResumen(BaseModel):
    """Secciones del resumen; se piden sin el campo 'resumen' para que el modelo las rellene."""
    objetivos: list[str] = Field(default_factory=list, description="Objetivos o metas del estudio.")
    metodologia: str = Field(default="", description="Metodologia, tecnicas o enfoque del estudio.")
    hallazgos: list[str] = Field(default_factory=list, description="Hallazgos o resultados principales.")
    limitaciones: list[str] = Field(default_factory=list, description="Limitaciones del estudio.")


class Entidades(BaseModel):
    """Metadatos bibliograficos del articulo."""
    titulo: str = ""
    autores: list[str] = Field(default_factory=list)
    anio: str = ""
    venue: str = Field(default="", description="Revista o congreso.")
    palabras_clave: list[str] = Field(default_factory=list)
    datasets: list[str] = Field(default_factory=list)
    metricas: list[str] = Field(default_factory=list)


class FichaComparativa(BaseModel):
    """Ficha de un documento; con dos de estas armo la comparacion."""
    objetivo: str = ""
    metodo: str = ""
    datos: str = ""
    resultados: str = ""


class Comparacion(BaseModel):
    """Resultado de comparar dos documentos (lo que se muestra en la tabla)."""
    objetivo_a: str = ""
    objetivo_b: str = ""
    metodo_a: str = ""
    metodo_b: str = ""
    datos_a: str = ""
    datos_b: str = ""
    resultados_a: str = ""
    resultados_b: str = ""
    conclusion: str = ""

    def filas(self):
        """Devuelve la comparacion como filas (aspecto, A, B) para mostrarla en tabla."""
        return [
            ("Objetivo", self.objetivo_a, self.objetivo_b),
            ("Metodo", self.metodo_a, self.metodo_b),
            ("Datos", self.datos_a, self.datos_b),
            ("Resultados", self.resultados_a, self.resultados_b),
        ]


class AgenteAcademico:
    """Agente que resume, compara y responde preguntas sobre documentos academicos."""

    def __init__(self, modelo=None):
        self.llm = ChatOllama(
            model=modelo or config.MODELO_TEXTO,
            base_url=config.OLLAMA_BASE_URL,
            temperature=config.TEMPERATURA,
            num_ctx=config.NUM_CTX,
            keep_alive=config.KEEP_ALIVE,
        )
        self.documento = ""
        self._historiales = {}      # historial de mensajes por sesion

    def cargar(self, ruta):
        """Lee un documento y lo guarda como contexto actual."""
        self.documento = ingest.cargar_documento(ruta)
        return self.documento

    def _estructurar(self, prompt, esquema, **kwargs):
        """Ejecuta un prompt y devuelve la respuesta en el esquema Pydantic indicado."""
        # with_structured_output obliga al modelo a rellenar el esquema y lo devuelve ya parseado
        chain = prompt | self.llm.with_structured_output(esquema)
        return chain.invoke(kwargs)

    def resumir(self, documento=None):
        """Resumen estructurado del documento.

        El resumen general y las secciones se piden por separado: si van en un mismo
        esquema, el modelo pequeno tiende a escribirlo todo en el resumen y deja
        vacias las demas secciones. Las secciones se reintentan si quedan huecos.
        """
        doc = documento if documento is not None else self.documento
        resumen = (prompts.PROMPT_RESUMEN | self.llm).invoke({"documento": doc}).content.strip()
        s = self._estructurar(prompts.PROMPT_SECCIONES, SeccionesResumen, documento=doc)
        if not (s.objetivos and s.metodologia and s.hallazgos and s.limitaciones):
            # Reintento con mas temperatura; se combinan para rellenar los huecos.
            alt = ChatOllama(model=config.MODELO_TEXTO, base_url=config.OLLAMA_BASE_URL,
                             temperature=0.5, num_ctx=config.NUM_CTX, keep_alive=config.KEEP_ALIVE)
            g = (prompts.PROMPT_SECCIONES | alt.with_structured_output(SeccionesResumen)).invoke(
                {"documento": doc})
            s = SeccionesResumen(
                objetivos=s.objetivos or g.objetivos,
                metodologia=s.metodologia or g.metodologia,
                hallazgos=s.hallazgos or g.hallazgos,
                limitaciones=s.limitaciones or g.limitaciones,
            )
        return ResumenArticulo(
            resumen=resumen, objetivos=s.objetivos, metodologia=s.metodologia,
            hallazgos=s.hallazgos, limitaciones=s.limitaciones)

    def extraer_entidades(self, documento=None):
        """Metadatos bibliograficos del documento."""
        doc = documento if documento is not None else self.documento
        return self._estructurar(prompts.PROMPT_ENTIDADES, Entidades, documento=doc)

    def _ficha(self, documento):
        """Extrae la ficha de un documento y reintenta si algun campo queda vacio."""
        f = self._estructurar(prompts.PROMPT_FICHA, FichaComparativa, documento=documento)
        if f.objetivo and f.metodo and f.datos and f.resultados:
            return f
        # Segundo intento con mas temperatura; se combinan para rellenar los huecos.
        alt = ChatOllama(model=config.MODELO_TEXTO, base_url=config.OLLAMA_BASE_URL,
                         temperature=0.5, num_ctx=config.NUM_CTX, keep_alive=config.KEEP_ALIVE)
        g = (prompts.PROMPT_FICHA | alt.with_structured_output(FichaComparativa)).invoke(
            {"documento": documento})
        return FichaComparativa(
            objetivo=f.objetivo or g.objetivo,
            metodo=f.metodo or g.metodo,
            datos=f.datos or g.datos,
            resultados=f.resultados or g.resultados,
        )

    def comparar(self, documento_a, documento_b):
        """Compara dos documentos.

        Se extrae una ficha de cada documento por separado (mas fiable con modelos
        pequenos) y luego se ensambla la tabla y se redacta la conclusion.
        """
        fa = self._ficha(documento_a)
        fb = self._ficha(documento_b)
        conclusion = (prompts.PROMPT_CONCLUSION | self.llm).invoke({
            "obj_a": fa.objetivo, "met_a": fa.metodo, "dat_a": fa.datos, "res_a": fa.resultados,
            "obj_b": fb.objetivo, "met_b": fb.metodo, "dat_b": fb.datos, "res_b": fb.resultados,
        }).content
        return Comparacion(
            objetivo_a=fa.objetivo, objetivo_b=fb.objetivo,
            metodo_a=fa.metodo, metodo_b=fb.metodo,
            datos_a=fa.datos, datos_b=fb.datos,
            resultados_a=fa.resultados, resultados_b=fb.resultados,
            conclusion=conclusion,
        )

    def preguntar(self, pregunta, session_id="default"):
        """Responde una pregunta sobre el documento manteniendo el contexto.

        Guarda el historial de la sesion y lo pasa al prompt, de forma que las
        preguntas de seguimiento resuelven referencias a turnos anteriores.
        """
        historial = self._historiales.setdefault(session_id, [])
        respuesta = (prompts.PROMPT_QA | self.llm).invoke({
            "pregunta": pregunta,
            "documento": self.documento,
            "historial": historial,
        })
        # guardo este turno para que la siguiente pregunta tenga el contexto
        historial.append(HumanMessage(content=pregunta))
        historial.append(AIMessage(content=respuesta.content))
        return respuesta.content

    def reiniciar_memoria(self, session_id="default"):
        """Borra el historial de una sesion."""
        self._historiales.pop(session_id, None)


def construir_agente_con_tools(agente):
    """Crea un agente de LangChain con herramientas que envuelven las funciones.

    Muestra el uso de agents y tools: el modelo elige que herramienta llamar segun
    lo que pida el usuario. El flujo principal sigue siendo el de AgenteAcademico.
    """
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.tools import tool

    @tool
    def resumir_documento(ruta: str) -> str:
        """Carga un documento y devuelve su resumen."""
        agente.cargar(ruta)
        return agente.resumir().model_dump_json()

    @tool
    def extraer_metadatos(ruta: str) -> str:
        """Carga un documento y extrae sus metadatos."""
        agente.cargar(ruta)
        return agente.extraer_entidades().model_dump_json()

    @tool
    def comparar_documentos(ruta_a: str, ruta_b: str) -> str:
        """Compara dos documentos."""
        doc_a = ingest.cargar_documento(ruta_a)
        doc_b = ingest.cargar_documento(ruta_b)
        return agente.comparar(doc_a, doc_b).model_dump_json()

    herramientas = [resumir_documento, extraer_metadatos, comparar_documentos]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Usa las herramientas para analizar los documentos que pida el "
                   "usuario. Responde en espanol."),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agente_lc = create_tool_calling_agent(agente.llm, herramientas, prompt)
    return AgentExecutor(agent=agente_lc, tools=herramientas, verbose=True,
                         max_iterations=5, handle_parsing_errors=True)
