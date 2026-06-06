import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Lazy-loaded globals
_embeddings = None
_COLLECTION_NAME = None

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
                # Quick permission sanity check query to ensure key is valid and active
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

def process_file(file_path: str):
    """
    Loads a PDF or Text file, splits it into chunks, and adds it to the PGVector store.
    """
    if file_path.endswith('.pdf'):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    pages = loader.load()
    
    # Balanced chunking
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(pages)
    
    if not docs:
        raise ValueError("No readable text found in the document. It might be a scanned image or empty.")
    
    embeddings, collection_name = get_embeddings_and_collection()
    
    # Save documents directly to PostgreSQL via PGVector
    from langchain_community.vectorstores.pgvector import PGVector
    PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=collection_name,
        connection_string=DB_URL,
    )
    
    return len(docs)

def get_retriever():
    """
    Returns a retriever for searching the vector store.
    """
    if not DB_URL:
        return None
    
    embeddings, collection_name = get_embeddings_and_collection()
    from langchain_community.vectorstores.pgvector import PGVector
    vectorstore = PGVector(
        collection_name=collection_name,
        connection_string=DB_URL,
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 5})

def search_vector_store(query: str):
    """
    Searches the vector store for relevant context.
    """
    retriever = get_retriever()
    if retriever:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    return "No context found."
