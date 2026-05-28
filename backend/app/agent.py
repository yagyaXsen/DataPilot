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
    return db.run(query)

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
    
    1. For financial reports/PDFs, always use the `knowledge_retrieval_tool`.
    2. Search for variations (e.g., "Revenue", "Income") if "Sales" isn't found.
    3. Be concise and accurate.
    
    Current Database Schema:
    {schema}
    """),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def ask_datapilot(user_input: str, chat_history=None):
    if chat_history is None:
        chat_history = []
    
    # Truncate history to save tokens
    chat_history = chat_history[-5:]
    
    schema = get_db_schema()
    response = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history,
        "schema": schema
    })
    return response["output"]
