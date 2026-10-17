"""
admin.py - Panel administrativo del Asistente Virtual FIME-UANL.
Ejecutar: streamlit run admin.py
"""

import os
import subprocess
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Panel Administrativo - Asistente FIME",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Panel Administrativo")
st.markdown("Gestión de la base de conocimiento del Asistente Virtual FIME-UANL")

st.divider()

# --- Métricas ---
st.header("📊 Estado del sistema")

col1, col2, col3 = st.columns(3)

with col1:
    num_docs = len(os.listdir("docs")) if os.path.exists("docs") else 0
    st.metric("📄 Documentos indexados", num_docs)

with col2:
    existe_db = os.path.exists("chroma_db")
    st.metric("💾 Base vectorial", "✅ Activa" if existe_db else "❌ No existe")

with col3:
    st.metric("🔄 Estado", "Listo" if existe_db and num_docs > 0 else "Pendiente")

st.divider()

# --- Reindexación ---
st.header("🔄 Reindexar base de conocimiento")
st.markdown("""
Si el sitio web de FIME ha sido actualizado, ejecuta este proceso para:
1. Volver a extraer la información del sitio web.
2. Regenerar los embeddings.
3. Actualizar la base vectorial.
""")

if st.button("🚀 Reindexar ahora", type="primary"):
    with st.spinner("Reindexando... Esto puede tomar varios minutos."):
        try:
            subprocess.run(["python", "scraper.py"], check=True)
            subprocess.run(["python", "vectorizar.py"], check=True)
            st.success("✅ Base de conocimiento reindexada exitosamente")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error durante la reindexación: {e}")

st.divider()

# --- Documentación ---
st.header("📖 Documentación")

with st.expander("¿Cómo funciona el asistente?"):
    st.markdown("""
    El asistente utiliza una arquitectura **RAG (Retrieval-Augmented Generation)**:

    1. **Scraping**: Se extrae información del sitio web de FIME.
    2. **Vectorización**: Los documentos se convierten en embeddings.
    3. **Almacenamiento**: Los vectores se guardan en ChromaDB.
    4. **Recuperación**: Cuando el usuario pregunta, se buscan los fragmentos más relevantes.
    5. **Generación**: El LLM (Ollama) genera una respuesta basada en esos fragmentos.
    """)

with st.expander("Solución de problemas"):
    st.markdown("""
    **El asistente no responde correctamente:**
    - Verifica que Ollama esté ejecutándose: `ollama serve`
    - Verifica que los modelos estén descargados: `ollama list`
    - Reindexa la base de conocimiento.

    **Error al cargar la base vectorial:**
    - Elimina la carpeta `chroma_db/` y vuelve a ejecutar `python vectorizar.py`.
    """)

st.divider()
st.caption("Asistente Virtual FIME-UANL | Panel Administrativo v1.0")