from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from app.database import file_to_sql
from app.vector_store import process_file
from app.agent import ask_datapilot
import shutil
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "DataPilot API is running!"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        filename_lower = file.filename.lower()
        
        if filename_lower.endswith(('.csv', '.xls', '.xlsx', '.json')):
            table_name = "".join(filter(str.isalnum, file.filename.split('.')[0])).lower()
            file_to_sql(file_path, table_name)
            return {"message": f"Structured file '{file.filename}' processed into table '{table_name}'"}
        
        elif filename_lower.endswith(('.pdf', '.txt')):
            num_chunks = process_file(file_path)
            return {"message": f"Unstructured file '{file.filename}' processed into {num_chunks} vector chunks"}
        
        return {"error": "Unsupported file format. Please upload CSV, XLSX, JSON, PDF, or TXT."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": f"Processing failed: {str(e)}"}

@app.post("/chat")
async def chat(message: str = Form(...)):
    try:
        response = ask_datapilot(message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
