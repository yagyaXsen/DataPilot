# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Robust embedding and collection selection with fallback verification
def initialize_embeddings_and_collection():
    if os.getenv("GOOGLE_API_KEY"):
        try:
            google_embed = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            # Quick permission sanity check query to ensure key is valid and active
            google_embed.embed_query("test query")
            print("Google Generative AI Embeddings initialized successfully.")
            return google_embed, "datapilot_gemini_vectors"
        except Exception as e:
            print(f"Google API Key failed verification: {str(e)}")
            print("Falling back to local BAAI/bge-small-en-v1.5 embeddings.")
            
    # Local fallback
    hf_embed = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return hf_embed, "datapilot_pdf_vectors"

embeddings, COLLECTION_NAME = initialize_embeddings_and_collection()

def process_file(file_path: str):
    """
    Loads a PDF or Text file, splits it into chunks, and adds it to the PGVector store.
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    pages = loader.load()
    
    # Balanced chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(pages)
    
    if not docs:
        raise ValueError("No readable text found in the document. It might be a scanned image or empty.")
    
    # Save documents directly to PostgreSQL via PGVector
    PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        collection_name=COLLECTION_NAME,
        connection_string=DB_URL,
    )
    
    return len(docs)

def get_retriever():
    """
    Returns a retriever for searching the vector store.
    """
    if not DB_URL:
        return None
    
    vectorstore = PGVector(
        collection_name=COLLECTION_NAME,
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
