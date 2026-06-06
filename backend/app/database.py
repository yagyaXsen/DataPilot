import pandas as pd
from sqlalchemy import create_engine, inspect
import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./datapilot.db")
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DB_URL)

def file_to_sql(file_path: str, table_name: str):
    """
    Reads a CSV, Excel, or JSON file and saves it as a table in the SQLite database.
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format for SQL conversion")

    # Clean column names
    df.columns = [str(c).lower().replace(' ', '_').replace('(', '').replace(')', '') for c in df.columns]
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    return table_name

def get_db_schema():
    """
    Returns the schema of the database for the LLM to understand.
    """
    inspector = inspect(engine)
    schema_info = ""
    for table_name in inspector.get_table_names():
        schema_info += f"Table: {table_name}\n"
        columns = inspector.get_columns(table_name)
        for column in columns:
            schema_info += f"  - {column['name']} ({column['type']})\n"
        schema_info += "\n"
    return schema_info

def run_query(query: str):
    """
    Executes a SQL query and returns the results as a list of dictionaries.
    """
    with engine.connect() as conn:
        result = conn.execute(query)
        return [dict(row) for row in result.mappings()]
