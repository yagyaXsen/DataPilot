# DataPilot 

DataPilot is a production-grade **Hybrid RAG (Retrieval-Augmented Generation)** data analysis assistant.  
It seamlessly handles both **structured data** (CSV, Excel, JSON) via an SQL Agent and **unstructured data** (PDF, TXT) via a Vector Search Engine — all through a single natural language interface.

---

## What Problem Does DataPilot Solve?

Imagine you want to answer this question:

> **"What were our Q1 sales, and what risks were identified in the quarterly report?"**

Normally, you'd need to open Excel for the numbers, open a PDF reader for the report, manually search both, then stitch the answer together yourself. DataPilot does all of that in one question.

Here is exactly how:

**Step 1 — You upload your files**

You drag a sales CSV and a quarterly report PDF into the app. The system looks at each file and asks: is this a number-type file or a words-type file?

**Step 2 — The system processes each file differently, automatically**

- The CSV → A tool called Pandas reads it, cleans up the column names, and saves it as a proper table inside a real database (like a mini Excel sheet, but a database).
- The PDF → A different tool reads all the text out of it, chops it into small chunks (like paragraphs), and converts each chunk into a kind of "fingerprint" (called an embedding) that captures its meaning. Those fingerprints get stored in a special database built for searching by meaning, not just keywords.

So now you have two databases: one for exact numbers, one for searchable document meaning.

**Step 3 — You ask your question in plain English**

You type the Q1 sales + risks question into the chat box. No SQL, no menus.

**Step 4 — The AI agent decides what to do**

This is the smart part. An AI model (LLaMA 3.3) reads your question and reasons about it almost like a person would:

- "Q1 sales" → that's a number → I should run a database query
- "risks identified in the report" → that's meaning/context → I should search the documents

It's not a hardcoded rule like "if question contains 'sales' do X" — the AI actually decides this itself based on understanding the question, which is why it can handle questions you never anticipated.

**Step 5 — It runs both tools and gets real results**

- For the sales part: it writes an actual SQL query (like `SELECT SUM(revenue) FROM sales WHERE quarter='Q1'`) and runs it against the real database. The number comes back exact — not guessed.
- For the risks part: it searches the document database for the chunks whose "meaning fingerprint" is closest to "risks in the report," and pulls out the actual relevant paragraphs.

**Step 6 — It combines both answers into one response**

The AI takes the exact sales number and the retrieved risk paragraphs, and writes you one clean, natural-language answer — citing both sources in a single reply.

---

## Features

| Feature | Description |
|---|---|
| **Hybrid Analysis** | Automatically routes questions to the right data source (SQL or Vector DB) |
| **SQL Agent** | Converts natural language to SQL queries via LLaMA 3.3-70B on Groq |
| **Vector Search** | Semantic search over PDFs using Gemini Embeddings + PGVector |
| **Smart Routing** | Dynamic tool selection — hides SQL tool when no structured data is loaded |
| **Multi-format** | Supports CSV, XLSX, XLS, JSON, PDF, TXT |
| **Tech Stack Page** | Built-in `/techstack` view with full architecture breakdown |

---

## System Architecture

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
│  └─────┬──────┘    │  (LLaMA 3.3-70B      │ │
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
│        │           ┌────────┐ ┌─────────┐   │
│        ▼           │Postgres│ │PGVector │   │
│  ┌───────────┐     │(SQLite)│ │(Gemini  │   │
│  │ PyPDF /   │     │        │ │Embed)   │   │
│  │ TextLoader│     └────────┘ └─────────┘   │
│  │ → Chunking│                              │
│  │ → Embed   │                              │
│  └───────────┘                              │
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

## Tech Stack

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
| Supabase | Managed cloud PostgreSQL host — provides the `DATABASE_URL` for both SQL and PGVector |
| PostgreSQL + PGVector | Underlying DB engine inside Supabase with `pgvector` extension for vector search |
| SQLite | Local SQL fallback when no `DATABASE_URL` is set |
| FAISS (CPU) | Local vector indexing fallback |

---

## Local Setup

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

## Deployment on Render

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

## Project Structure

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

## How to Use

1. **Upload** — Drop a CSV/Excel/JSON for SQL analysis, or a PDF/TXT for semantic search
2. **Ask** — Type any question: *"What is the total revenue by region?"* or *"Summarize the key risks in the report"*
3. **Explore** — Click **Tech Stack** in the sidebar to see the full architecture

---

*Built with  using FastAPI · LangChain · Groq · PGVector · React · Vite*
