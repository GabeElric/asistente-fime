"""
motor_ia.py - Motor de inteligencia artificial (RAG + Ollama) con LCEL.
Ejecutar: python motor_ia.py
"""

import warnings

# Silenciar advertencias de deprecación de LangChain (siguen funcionando)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document


CHROMA_DIR = "chroma_db"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3"
TOP_K = 3

SYSTEM_PROMPT = """Eres un asistente virtual de la Facultad de Ingeniería Mecánica y Eléctrica (FIME) de la UANL.
Tu única función es responder preguntas basándote EXCLUSIVAMENTE en la información proporcionada en el contexto.

Reglas:
- Si la respuesta está en el contexto, responde de forma clara y concisa en español.
- Si la respuesta NO está en el contexto, di: "Lo siento, no tengo información sobre eso. Te recomiendo consultar directamente el sitio web de FIME o acudir a Servicios Escolares."
- No inventes información.
- Mantén un tono amable y profesional.

Contexto:
{context}
"""

store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Obtiene o crea el historial de una sesión."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def formatear_documentos(docs: list[Document]) -> str:
    """Convierte una lista de documentos en un solo string de contexto."""
    if not docs:
        return "No se encontró información relevante en la base de conocimiento."
    return "\n\n".join(doc.page_content for doc in docs)


def extraer_pregunta(x) -> str:
    """
    Extrae el texto de la pregunta del diccionario de entrada.
    Acepta tanto un dict {'input': '...'} como un string directo.
    """
    if isinstance(x, dict):
        return x.get("input", "")
    return str(x)


def crear_motor():
    """Crea y devuelve la cadena RAG con memoria conversacional."""
    print("=" * 50)
    print("MOTOR DE IA - ASISTENTE FIME-UANL")
    print("=" * 50)

    # 1. Cargar embeddings y base vectorial
    print("\n📂 Cargando base vectorial...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="fime_knowledge",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    print("  ✅ Base vectorial cargada")

    # 2. Configurar LLM
    print(f"\n🧠 Cargando modelo '{LLM_MODEL}' desde Ollama...")
    llm = ChatOllama(model=LLM_MODEL, temperature=0.3)
    print("  ✅ Modelo cargado")

    # 3. Prompt con historial y contexto
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    # 4. Cadena RAG con LCEL
    #    RunnablePassthrough.assign conserva 'input' y 'chat_history'
    #    y añade 'context' con los documentos recuperados.
    rag_chain = (
        RunnablePassthrough.assign(
            context=(
                RunnableLambda(extraer_pregunta)
                | retriever
                | RunnableLambda(formatear_documentos)
            )
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    # 5. Envolver con memoria conversacional
    chain_with_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    print("  ✅ Cadena RAG con memoria lista")
    return chain_with_history, vectorstore


def main():
    """Función principal para probar el motor desde la terminal."""
    chain, vectorstore = crear_motor()
    session_id = "sesion-prueba"

    print("\n" + "=" * 50)
    print("MODO DE PRUEBA - Escribe 'salir' para terminar")
    print("=" * 50)

    while True:
        pregunta = input("\n🧑 Tú: ").strip()

        if not pregunta or pregunta.lower() in ("salir", "exit", "quit"):
            print("👋 ¡Hasta luego!")
            break

        try:
            respuesta = chain.invoke(
                {"input": pregunta},
                config={"configurable": {"session_id": session_id}},
            )
            print(f"\n🤖 Asistente: {respuesta}")

            # Mostrar fuentes consultadas (opcional)
            docs = vectorstore.similarity_search(pregunta, k=TOP_K)
            if docs:
                print(f"\n   📚 Fuentes consultadas ({len(docs)}):")
                for i, d in enumerate(docs, 1):
                    fuente = d.metadata.get("source", "desconocida")
                    print(f"   [{i}] {fuente}")

        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()