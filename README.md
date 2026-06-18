# DataPilot 

DataPilot is a production-grade **Hybrid RAG (Retrieval-Augmented Generation)** data analysis assistant.  
It seamlessly handles both **structured data** (CSV, Excel, JSON) via an SQL Agent and **unstructured data** (PDF, TXT) via a Vector Search Engine — all through a single natural language interface.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Hybrid Analysis** | Automatically routes questions to the right data source (SQL or Vector DB) |
| **SQL Agent** | Converts natural language to SQL queries via LLaMA 3.3-70B on Groq |
| **Vector Search** | Semantic search over PDFs using Gemini Embeddings + PGVector |
| **Smart Routing** | Dynamic tool selection — hides SQL tool when no structured data is loaded |
| **Multi-format** | Supports CSV, XLSX, XLS, JSON, PDF, TXT |
| **Tech Stack Page** | Built-in `/techstack` view with full architecture breakdown |

---

## 🏗️ System Architecture

```
User (React UI)
      │
      ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                │
│                                             │
│  POST /upload          POST /chat           │
│       │                      │              │
│       ▼                      ▼              │
│  ┌────────────┐    ┌──────────────────────┐ │
│  │ File Router│    │  LangChain Agent     │ │
│  └─────┬──────┘    │  (LLaMA 3.3-70B     │ │
│        │           │   via Groq)          │ │
│   CSV/Excel/JSON   └──────────┬───────────┘ │
│        │                      │             │
│        ▼              ┌───────┴────────┐    │
│  ┌───────────┐        │ Tool Selection │    │
│  │  Pandas   │        └───┬───────┬────┘    │
│  │  + SQLAlch│            │       │         │
│  │  → SQL DB │            ▼       ▼         │
│  └───────────┘    sql_query  knowledge_     │
│                     _tool    retrieval_tool │
│        │                │         │         │
│   PDF/TXT               ▼         ▼         │
│        │           ┌────────┐ ┌─────────┐  │
│        ▼           │Postgres│ │PGVector │  │
│  ┌───────────┐     │(SQLite)│ │(Gemini  │  │
│  │ PyPDF /   │     │        │ │Embed)   │  │
│  │ TextLoader│     └────────┘ └─────────┘  │
│  │ → Chunking│                             │
│  │ → Embed   │                             │
│  └───────────┘                             │
└─────────────────────────────────────────────┘
```

### Three Core Pillars

**Pillar 1 — Data Ingestion & Processing Engine**
- Structured files (CSV/Excel/JSON) → Pandas ETL → SQLAlchemy → PostgreSQL/SQLite table
- Unstructured files (PDF/TXT) → PyPDF → RecursiveCharacterTextSplitter (1000 char chunks, 100 overlap) → Gemini Embeddings → PGVector

**Pillar 2 — Hybrid AI Agent**
- LangChain `create_tool_calling_agent` with LLaMA 3.3-70B (Groq) as the reasoning LLM
- Two tools: `sql_query_tool` (structured) and `knowledge_retrieval_tool` (unstructured)
- Dynamic tool selection: if no SQL tables exist, the SQL tool is hidden from the agent
- Chat history truncated to last 5 turns to optimize token usage

**Pillar 3 — React Frontend**
- Minimal, dark-themed UI with Framer Motion animations
- Sidebar with file source tracking and Tech Stack navigation
- `/techstack` page with full architecture breakdown and tech cards

---

## 🛠️ Tech Stack

### Frontend
| Library | Version | Role |
|---|---|---|
| React | 19 | UI framework |
| Vite | 8 | Build tool & dev server |
| TailwindCSS | v4 | Utility-first styling |
| Framer Motion | 12 | Animations |
| Lucide React | Latest | Icons |
| Recharts | 3 | Data visualization |
| Axios | 1.x | HTTP client |

### Backend
| Library | Role |
|---|---|
| FastAPI | REST API framework |
| Uvicorn / Gunicorn | ASGI/WSGI server |
| SQLAlchemy | ORM + DB engine |
| Pandas + openpyxl | ETL for structured files |
| PyPDF | PDF text extraction |
| python-dotenv | Environment management |
| psycopg2-binary | PostgreSQL adapter |

### AI & LLM
| Component | Role |
|---|---|
| LangChain | Agent orchestration framework |
| LangChain-Groq | LLaMA 3.3-70B (ultra-fast inference) |
| Google Gemini Embeddings | `gemini-embedding-001` for semantic search |
| Sentence-Transformers | Local fallback (BAAI/bge-small-en-v1.5) |

### Databases
| DB | Purpose |
|---|---|
| PostgreSQL + PGVector | Production vector store |
| SQLite | Local SQL fallback |
| FAISS (CPU) | Local vector indexing fallback |

---

## ⚡ Local Setup

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```env
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://user:pass@host/db   # or leave empty for SQLite
```

Run:
```bash
python main.py
# → Running on http://0.0.0.0:8001
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
# → Running on http://localhost:5173
```

---

## 🌐 Deployment on Render

### Backend (Web Service)
| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app` |
| Env Vars | `GOOGLE_API_KEY`, `GROQ_API_KEY`, `DATABASE_URL` |

### Frontend (Static Site)
| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Publish Directory | `dist` |
| Env Vars | `VITE_API_URL` → your backend Render URL |

---

## 📁 Project Structure

```
DataPilot/
├── backend/
│   ├── main.py               # FastAPI app, /upload and /chat endpoints
│   ├── requirements.txt      # Python dependencies
│   ├── Procfile              # Render deployment config
│   └── app/
│       ├── agent.py          # LangChain agent + tool definitions
│       ├── vector_store.py   # PGVector + Gemini Embeddings pipeline
│       └── database.py       # SQLAlchemy + Pandas ETL pipeline
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main chat interface
│   │   ├── TechStack.jsx     # Tech stack & architecture page
│   │   └── index.css         # TailwindCSS v4 theme
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 💡 How to Use

1. **Upload** — Drop a CSV/Excel/JSON for SQL analysis, or a PDF/TXT for semantic search
2. **Ask** — Type any question: *"What is the total revenue by region?"* or *"Summarize the key risks in the report"*
3. **Explore** — Click **Tech Stack** in the sidebar to see the full architecture

---

*Built with ❤️ using FastAPI · LangChain · Groq · PGVector · React · Vite*
