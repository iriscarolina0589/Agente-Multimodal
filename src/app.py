"""Interfaz web del agente de documentos académicos (Streamlit)."""

import tempfile
from pathlib import Path

import streamlit as st

import config
from agent import AgenteAcademico
from ingest import cargar_documento

st.set_page_config(page_title="Agente Multimodal", page_icon="🅐", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
      html, body, [class*="css"], .stApp, button, input, textarea, .stMarkdown {
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
      }
      #MainMenu, footer { visibility: hidden; }
      [data-testid="stHeader"] { background: transparent; }
      .block-container { padding-top: 2.4rem; max-width: 1080px; }
      .titulo { font-size: 2rem; font-weight: 700; color: #f3f5f9; letter-spacing: -.6px; margin: 0; }
      .titulo .punto { color: #10a37f; }
      .subtitulo { color: #8b949e; font-size: .92rem; margin: .25rem 0 1.6rem 0; }
      .etq { color: #10a37f; font-weight: 600; font-size: .76rem;
             text-transform: uppercase; letter-spacing: .07em; }
      [data-testid="stVerticalBlockBorderWrapper"] {
        background: #161b22; border: 1px solid #232b36 !important; border-radius: 14px;
      }
      .stTabs [data-baseweb="tab"] { font-weight: 600; }
      .stButton button { border-radius: 10px; font-weight: 600; }
      [data-testid="stChatMessage"] {
        background: #161b22; border: 1px solid #232b36; border-radius: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="titulo">Agente Multimodal</p>', unsafe_allow_html=True)

# # Estado de la sesión.
if "agente" not in st.session_state:
    st.session_state.agente = AgenteAcademico()
if "doc" not in st.session_state:
    st.session_state.doc = None
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "cache" not in st.session_state:
    st.session_state.cache = {}

agente: AgenteAcademico = st.session_state.agente


def guardar_temporal(archivo):
    """Guarda el archivo subido temporalmente y devuelve la ruta."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(archivo.name).suffix) as tmp:
        tmp.write(archivo.getbuffer())
        return tmp.name

# Etiqueta visual para títulos en la interfaz
def etiqueta(texto):
    st.markdown(f'<span class="etq">{texto}</span>', unsafe_allow_html=True)

# Carga de documentos
with st.sidebar:
    st.subheader("Documento")
    archivo = st.file_uploader("Sube un PDF, CSV, TXT o imagen",
                               type=["pdf", "csv", "txt", "md", "png", "jpg", "jpeg"])
    if archivo and st.button("Cargar", use_container_width=True, type="primary"):
        with st.spinner("Extrayendo el contenido..."):
            agente.cargar(guardar_temporal(archivo))
        agente.reiniciar_memoria()
        st.session_state.doc = archivo.name
        st.session_state.mensajes = []
        st.session_state.cache = {}

    st.divider()
    st.subheader("Comparar")
    archivo_b = st.file_uploader("Segundo documento", type=["pdf", "txt", "md"], key="doc_b")

    st.divider()
    st.caption("Estado")
    st.write("Modelo:", config.MODELO_TEXTO)
    if st.session_state.doc:
        st.success(f"Cargado: {st.session_state.doc}")
    else:
        st.info("Sin documento cargado")


if not st.session_state.doc:
    st.info("Sube un documento en el panel de la izquierda para empezar.")
    st.stop()

tab_res, tab_meta, tab_cmp, tab_chat = st.tabs(
    ["Resumen", "Metadatos", "Comparativa", "Preguntas"])
# Genera y muestra el resumen del documento
with tab_res:
    if st.button("Generar resumen"):
        with st.spinner("Analizando el documento..."):
            st.session_state.cache["resumen"] = agente.resumir()
    r = st.session_state.cache.get("resumen")
    if r:
        with st.container(border=True):
            etiqueta("Resumen")
            st.write(r.resumen)
        col1, col2 = st.columns(2)
        with col1.container(border=True):
            etiqueta("Objetivos")
            for o in r.objetivos:
                st.markdown(f"- {o}")
        with col2.container(border=True):
            etiqueta("Hallazgos")
            for h in r.hallazgos:
                st.markdown(f"- {h}")
        with st.container(border=True):
            etiqueta("Metodología")
            st.write(r.metodologia)
        with st.container(border=True):
            etiqueta("Limitaciones")
            for l in r.limitaciones:
                st.markdown(f"- {l}")
# Extrae información bibliográfica del documento
with tab_meta:
    if st.button("Extraer metadatos"):
        with st.spinner("Extrayendo metadatos..."):
            st.session_state.cache["meta"] = agente.extraer_entidades()
    e = st.session_state.cache.get("meta")
    if e:
        col1, col2 = st.columns(2)
        col1.metric("Año", e.anio or "-")
        col2.metric("Publicación", e.venue or "-")
        with st.container(border=True):
            etiqueta("Título"); st.write(e.titulo or "-")
            etiqueta("Autores"); st.write(", ".join(e.autores) or "-")
            etiqueta("Palabras clave"); st.write(", ".join(e.palabras_clave) or "-")
            etiqueta("Datasets"); st.write(", ".join(e.datasets) or "-")
            etiqueta("Métricas"); st.write(", ".join(e.metricas) or "-")
# Comparación entre dos documentos
with tab_cmp:
    if not archivo_b:
        st.info("Sube un segundo documento en el panel lateral para comparar.")
    elif st.button("Comparar documentos"):
        with st.spinner("Comparando..."):
            doc_b = cargar_documento(guardar_temporal(archivo_b))
            st.session_state.cache["cmp"] = agente.comparar(agente.documento, doc_b)
    comp = st.session_state.cache.get("cmp")
    if comp:
        st.dataframe(
            [{"Aspecto": a, "Documento A": da, "Documento B": db} for a, da, db in comp.filas()],
            use_container_width=True, hide_index=True)
        with st.container(border=True):
            etiqueta("Conclusión")
            st.write(comp.conclusion)
# Chat con memoria sobre el documento
with tab_chat:
    for m in st.session_state.mensajes:
        st.chat_message(m["rol"]).write(m["texto"])
    if pregunta := st.chat_input("Pregunta algo sobre el documento..."):
        st.session_state.mensajes.append({"rol": "user", "texto": pregunta})
        st.chat_message("user").write(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = agente.preguntar(pregunta)
            st.write(respuesta)
        st.session_state.mensajes.append({"rol": "assistant", "texto": respuesta})
