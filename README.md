# DataPilot 

DataPilot is a powerful AI-driven data analysis assistant that handles both **structured data** (CSV, Excel, JSON) and **unstructured data** (PDF, TXT) using a hybrid RAG (Retrieval-Augmented Generation) architecture.

## Features
- **Hybrid Analysis**: Seamlessly switch between querying SQL databases and searching through large PDF reports.
- **SQL Agent**: Automatically converts your natural language questions into SQL queries to analyze spreadsheets.
- **Vector Search**: Uses FAISS and Gemini Embeddings to extract insights from 100+ page documents.
- **Modern UI**: A premium, responsive interface built with React and sleek CSS.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, LangChain
- **AI Engine**: Google Gemini (Flash 1.5)
- **Database**: SQLite (Structured) & FAISS (Unstructured)
- **Frontend**: React, Vite, Axios

## Local Setup

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend` folder:
```env
GOOGLE_API_KEY=your_gemini_api_key
```
Run the server:
```bash
python main.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment on Render

### Backend Setup:
1. Create a new **Web Service** on Render.
2. **Root Directory**: `backend`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app`
5. **Env Vars**: Add `GOOGLE_API_KEY`.

### Frontend Setup:
1. Create a new **Static Site** on Render.
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build`
4. **Publish Directory**: `dist`
5. **Env Vars**: Add `VITE_API_URL` pointing to your backend URL.

## How to Use
1. **Upload**: Drag and drop a CSV or a large PDF.
2. **Analyze**: Ask questions like *"What were the total sales in the North region?"* or *"Summarize the financial risks mentioned in the annual report."*
3. **Visualize**: DataPilot will provide structured answers and context-aware insights.
