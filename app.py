"""
app.py - Interfaz de chat con Streamlit, estilo institucional FIME-UANL.
Ejecutar: streamlit run app.py
"""

import uuid
import streamlit as st
from motor_ia import crear_motor

# --- Configuración de la página ---
st.set_page_config(
    page_title="Asistente Virtual FIME-UANL",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Estilos personalizados (verde institucional + blanco, alto contraste) ---
st.markdown("""
<style>
    /* Fondo general blanco */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Texto general oscuro para contraste sobre blanco */
    html, body, [class*="css"] {
        color: #1A1A1A;
    }

    /* Encabezado principal: fondo verde oscuro, texto blanco */
    .header-container {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        padding: 2rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(27, 94, 32, 0.25);
    }

    .header-container h1 {
        color: #FFFFFF !important;
        font-size: 1.9rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .header-container p {
        color: #E8F5E9 !important;
        font-size: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    /* Subtítulo bajo el encabezado */
    .subtitle {
        text-align: center;
        color: #1B5E20 !important;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }

    /* Mensajes del chat: contenedores con contraste garantizado */
    .stChatMessage {
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
    }

    /* Texto dentro de cualquier mensaje */
    .stChatMessage p,
    .stChatMessage li,
    .stChatMessage span,
    .stChatMessage div {
        color: #1A1A1A !important;
    }

    /* Mensaje del usuario: fondo verde claro */
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D32;
    }

    /* Mensaje del asistente: fondo gris muy claro */
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
        background-color: #F5F5F5;
        border-left: 4px solid #1B5E20;
    }

    /* Caja de entrada de chat */
    .stChatInputContainer textarea {
        border: 2px solid #2E7D32 !important;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        color: #1A1A1A !important;
    }

    .stChatInputContainer textarea::placeholder {
        color: #6B6B6B !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: #1B5E20 !important;
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.25) !important;
    }

    /* Botones: verde con texto blanco */
    .stButton > button {
        background-color: #2E7D32 !important;
        color: #FFFFFF !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #1B5E20 !important;
        color: #FFFFFF !important;
    }

    .stButton > button p,
    .stButton > button span {
        color: #FFFFFF !important;
    }

    /* Sidebar: fondo verde muy claro, texto oscuro */
    section[data-testid="stSidebar"] {
        background-color: #F1F8E9;
        border-right: 3px solid #2E7D32;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #1B5E20 !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #1A1A1A !important;
    }

    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {
        color: #4A4A4A !important;
    }

    /* Expander (fuentes consultadas) */
    .streamlit-expanderHeader {
        background-color: #E8F5E9 !important;
        color: #1B5E20 !important;
        font-weight: 600;
        border-radius: 6px;
    }

    .streamlit-expanderHeader p,
    .streamlit-expanderHeader span {
        color: #1B5E20 !important;
    }

    .streamlit-expanderContent {
        background-color: #FAFAFA !important;
        color: #1A1A1A !important;
    }

    .streamlit-expanderContent p,
    .streamlit-expanderContent span,
    .streamlit-expanderContent div {
        color: #1A1A1A !important;
    }

    /* Alertas y mensajes de error */
    .stAlert p,
    .stAlert span,
    .stAlert div {
        color: #1A1A1A !important;
    }

    /* Spinner */
    .stSpinner > div {
        color: #2E7D32 !important;
    }

    /* Pie de página */
    .footer {
        text-align: center;
        color: #1B5E20 !important;
        font-size: 0.85rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #C8E6C9;
        font-weight: 500;
    }

    /* Separadores del sidebar */
    section[data-testid="stSidebar"] hr {
        border-color: #C8E6C9;
    }

    /* Encabezado del sidebar personalizado */
    .sidebar-header h2 {
        color: #1B5E20 !important;
        margin-bottom: 0.2rem;
    }

    .sidebar-header p {
        color: #2E7D32 !important;
        font-size: 0.85rem;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Encabezado institucional ---
st.markdown("""
<div class="header-container">
    <h1>🎓 Asistente Virtual FIME-UANL</h1>
    <p>Facultad de Ingeniería Mecánica y Eléctrica · Universidad Autónoma de Nuevo León</p>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<p class="subtitle">Pregúntame sobre trámites, planes de estudio, becas, titulación y más.</p>',
    unsafe_allow_html=True
)

# --- Inicializar el motor RAG (solo una vez) ---
@st.cache_resource
def inicializar_motor():
    return crear_motor()

with st.spinner("Cargando el asistente... (esto puede tomar unos segundos)"):
    qa_chain, vectorstore = inicializar_motor()

# --- Inicializar historial de chat y session_id ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- Mostrar historial ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Entrada del usuario ---
if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                respuesta = qa_chain.invoke(
                    {"input": prompt},
                    config={
                        "configurable": {
                            "session_id": st.session_state.session_id
                        }
                    }
                )

                st.markdown(respuesta)

                # Fuentes consultadas
                docs = vectorstore.similarity_search(prompt, k=3)
                if docs:
                    with st.expander("📚 Ver fuentes consultadas"):
                        for i, doc in enumerate(docs, 1):
                            fuente = doc.metadata.get("source", "desconocida")
                            st.markdown(f"**[{i}]** {fuente}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": respuesta}
                )

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

# --- Barra lateral ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header" style="text-align:center; padding: 1rem 0;">
        <h2>🎓 FIME-UANL</h2>
        <p>Asistente Virtual</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### ℹ️ Información")
    st.markdown("""
    Este asistente responde preguntas basándose en la información pública del sitio web oficial de FIME.

    **Temas disponibles:**
    - Trámites escolares
    - Inscripción y preinscripción
    - Titulación
    - Becas
    - Planes de estudio
    - Reglamentos
    - Calendarios
    """)

    st.markdown("---")

    st.markdown("### ⚠️ Nota")
    st.caption(
        "Si la respuesta no está en la base de conocimiento, "
        "el asistente te recomendará acudir a Servicios Escolares."
    )

    st.markdown("---")

    st.caption(f"🔐 Sesión: `{st.session_state.session_id[:8]}...`")

    if st.button("🗑 Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- Pie de página ---
st.markdown("""
<div class="footer">
    Asistente Virtual FIME-UANL · Proyecto académico · 2026
</div>
""", unsafe_allow_html=True)