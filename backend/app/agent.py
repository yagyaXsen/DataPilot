from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from .database import get_db_schema, engine
from .vector_store import search_vector_store
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv()

db = SQLDatabase(engine)

@tool
def sql_query_tool(query: str):
    """Executes SQL queries against structured data (CSV/Excel/JSON)."""
    schema = get_db_schema()
    if schema == "No tables available.":
        return "CRITICAL ERROR: The database is completely empty. There are no tables to query. You MUST use the knowledge_retrieval_tool to answer the user's question from the PDFs."
    
    try:
        return db.run(query)
    except Exception as e:
        return f"SQL Error: {str(e)}. Please check the schema and try again or use the knowledge_retrieval_tool."

@tool
def knowledge_retrieval_tool(query: str):
    """Searches uploaded PDFs and text documents for context."""
    return search_vector_store(query)

tools = [sql_query_tool, knowledge_retrieval_tool]

# Using Groq for lightning-fast inference
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are DataPilot, a smart data assistant. 
    You help users analyze both structured (SQL) and unstructured (PDF) data.
    
    CRITICAL RULES:
    1. If the Database Schema says 'No tables available', you MUST NOT use the `sql_query_tool`. You must use the `knowledge_retrieval_tool` instead.
    2. NEVER hallucinate or invent table names. ONLY write SQL for tables that explicitly exist in the schema below.
    3. If the user asks about documents, reports, or PDFs, always use the `knowledge_retrieval_tool`.
    
    Current Database Schema:
    {schema}
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def ask_datapilot(user_input: str, chat_history=None):
    if chat_history is None:
        chat_history = []
    
    # Truncate history to save tokens
    chat_history = chat_history[-5:]
    
    schema = get_db_schema()
    
    # DYNAMIC TOOL SELECTION
    # If there are no CSVs uploaded, physically hide the SQL tool from the AI
    active_tools = [knowledge_retrieval_tool]
    if schema != "No tables available.":
        active_tools.append(sql_query_tool)
        
    # Re-build agent for this specific request with the allowed tools
    agent = create_tool_calling_agent(llm, active_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=active_tools, verbose=True)
    
    response = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history,
        "schema": schema
    })
    return response["output"]
