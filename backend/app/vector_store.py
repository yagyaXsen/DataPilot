import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# FAISS local index path (used when Supabase/PGVector is unreachable)
FAISS_INDEX_PATH = "faiss_index"

# Lazy-loaded globals
_embeddings = None
_COLLECTION_NAME = None
_use_faiss = False   # flips to True if PGVector connection fails locally


def get_embeddings_and_collection():
    """
    Lazy-loads and initializes the embedding model and collection name.
    """
    global _embeddings, _COLLECTION_NAME
    if _embeddings is None:
        if os.getenv("GOOGLE_API_KEY"):
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                google_embed = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
                # Quick permission sanity check
                google_embed.embed_query("test query")
                print("Google Generative AI Embeddings initialized successfully.")
                _embeddings = google_embed
                _COLLECTION_NAME = "datapilot_gemini_vectors"
                return _embeddings, _COLLECTION_NAME
            except Exception as e:
                print(f"Google API Key failed verification: {str(e)}")
                if os.getenv("RENDER"):
                    raise RuntimeError(
                        "CRITICAL ERROR: The provided GOOGLE_API_KEY is invalid or has been denied access by Google. "
                        "In production on Render, local Hugging Face fallback is disabled to prevent "
                        "Out of Memory (OOM) crashes (>512MB RAM limit)."
                    ) from e
                print("Falling back to local BAAI/bge-small-en-v1.5 embeddings.")

        # Local fallback for development environment only
        if os.getenv("RENDER"):
            raise RuntimeError(
                "CRITICAL ERROR: GOOGLE_API_KEY is not defined in the environment. "
                "Production on Render requires Google Gemini Embeddings to stay within memory limits."
            )

        from langchain_community.embeddings import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        _COLLECTION_NAME = "datapilot_pdf_vectors"

    return _embeddings, _COLLECTION_NAME


def _can_reach_pgvector():
    """
    Quick probe to check if the PGVector / Supabase DB is reachable.
    Returns True if reachable, False if network error (e.g. IPv6 unreachable locally).
    """
    if not DB_URL:
        return False
    try:
        import sqlalchemy
        engine = sqlalchemy.create_engine(DB_URL, connect_args={"connect_timeout": 5})
        with engine.connect():
            pass
        return True
    except Exception as e:
        print(f"[VectorStore] PGVector probe failed ({type(e).__name__}). "
              f"Switching to local FAISS fallback. Error: {e}")
        return False


def process_file(file_path: str):
    """
    Loads a PDF or Text file, splits it into chunks, then stores in:
      - PGVector (Supabase) if reachable  [production / good network]
      - FAISS local index if not reachable [local dev with IPv6 issues]
    """
    global _use_faiss

    if file_path.endswith('.pdf'):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format")

    pages = loader.load()

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(pages)

    if not docs:
        raise ValueError("No readable text found in the document. It might be a scanned image or empty.")

    embeddings, collection_name = get_embeddings_and_collection()

    # Try PGVector (Supabase) first; fall back to FAISS on network failure
    if DB_URL and not _use_faiss:
        if _can_reach_pgvector():
            try:
                from langchain_community.vectorstores.pgvector import PGVector
                PGVector.from_documents(
                    embedding=embeddings,
                    documents=docs,
                    collection_name=collection_name,
                    connection_string=DB_URL,
                )
                print(f"[VectorStore] Stored {len(docs)} chunks in Supabase PGVector.")
                return len(docs)
            except Exception as e:
                print(f"[VectorStore] PGVector write failed: {e}. Falling back to FAISS.")
                _use_faiss = True
        else:
            _use_faiss = True

    # FAISS local fallback
    print("[VectorStore] Using local FAISS index.")
    from langchain_community.vectorstores import FAISS

    if os.path.exists(FAISS_INDEX_PATH):
        # Load existing index and add new docs
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        vectorstore.add_documents(docs)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"[VectorStore] Stored {len(docs)} chunks in local FAISS index.")
    return len(docs)


def get_retriever():
    """
    Returns a retriever — PGVector (Supabase) if reachable, else local FAISS.
    """
    global _use_faiss
    embeddings, collection_name = get_embeddings_and_collection()

    # Try PGVector
    if DB_URL and not _use_faiss:
        if _can_reach_pgvector():
            try:
                from langchain_community.vectorstores.pgvector import PGVector
                vectorstore = PGVector(
                    collection_name=collection_name,
                    connection_string=DB_URL,
                    embedding_function=embeddings,
                )
                return vectorstore.as_retriever(search_kwargs={"k": 5})
            except Exception as e:
                print(f"[VectorStore] PGVector retriever failed: {e}. Falling back to FAISS.")
                _use_faiss = True
        else:
            _use_faiss = True

    # FAISS local fallback
    if os.path.exists(FAISS_INDEX_PATH):
        from langchain_community.vectorstores import FAISS
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        return vectorstore.as_retriever(search_kwargs={"k": 5})

    return None


def search_vector_store(query: str):
    """
    Searches the vector store (PGVector or FAISS) for relevant context.
    """
    retriever = get_retriever()
    if retriever:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    return "No context found. Please upload a PDF or TXT file first."
