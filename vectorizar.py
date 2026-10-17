"""
vectorizar.py - Crea la base de conocimiento vectorial con ChromaDB.
Ejecutar: python vectorizar.py
"""

import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Configuración
DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"
EMBED_MODEL = "nomic-embed-text"  # Modelo de embeddings de Ollama
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def main():
    print("=" * 50)
    print("VECTORIZACIÓN DE DOCUMENTOS")
    print("=" * 50)

    # 1. Verificar que existan documentos
    if not os.path.exists(DOCS_DIR) or not os.listdir(DOCS_DIR):
        print(f"No hay documentos en '{DOCS_DIR}/'. Ejecuta primero scraper.py")
        return

    # 2. Cargar documentos
    print(f"\nCargando documentos de '{DOCS_DIR}/'...")
    loader = DirectoryLoader(
        DOCS_DIR,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documentos = loader.load()
    print(f"  ✅ {len(documentos)} documentos cargados")

    # 3. Dividir en fragmentos
    print(f"\n✂️ Dividiendo en fragmentos (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    fragmentos = splitter.split_documents(documentos)
    print(f"   {len(fragmentos)} fragmentos generados")

    # Crear embeddings y almacenar en ChromaDB
    print(f"\n Generando embeddings con '{EMBED_MODEL}'...")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    print(f" Almacenando en ChromaDB ('{CHROMA_DIR}/')...")
    if os.path.exists(CHROMA_DIR):
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print("  🗑 Base anterior eliminada")

    vectorstore = Chroma.from_documents(
        documents=fragmentos,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="fime_knowledge"
    )

    print(f"\n Base vectorial creada exitosamente")
    print(f"    Fragmentos indexados: {len(fragmentos)}")
    print(f"    Ubicación: {CHROMA_DIR}/")

    # 5. Prueba de búsqueda
    print("\n🔍 Prueba de búsqueda semántica:")
    query = "¿Cómo me inscribo?"
    resultados = vectorstore.similarity_search(query, k=2)
    for i, doc in enumerate(resultados, 1):
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  [{i}] {preview}...")


if __name__ == "__main__":
    main()