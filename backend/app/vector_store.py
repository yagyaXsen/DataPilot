# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_PATH = "faiss_index"

def process_file(file_path: str):
    """
    Loads a PDF or Text file, splits it into chunks, and adds it to the FAISS vector store.
    Uses Gemini Cloud Embeddings for memory efficiency (required for Render).
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
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(VECTOR_DB_PATH):
        vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(docs)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)
    
    vectorstore.save_local(VECTOR_DB_PATH)
    return len(docs)

def get_retriever():
    """
    Returns a retriever for searching the vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if os.path.exists(VECTOR_DB_PATH):
        vectorstore = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        return vectorstore.as_retriever(search_kwargs={"k": 5})
    return None

def search_vector_store(query: str):
    """
    Searches the vector store for relevant context.
    """
    retriever = get_retriever()
    if retriever:
        docs = retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs])
    return "No context found."
