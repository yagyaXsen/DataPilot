# DataPilot System Architecture & Workflow Documentation

This document provides an in-depth explanation of the DataPilot system. It answers why we chose specific technologies, how the system functions under the hood, and provides a detailed walkthrough of the user workflow.

## 1. The Core Problem

Knowledge workers and data analysts facing huge amounts of information experience massive friction. They have to:

- Write complex SQL queries or advanced Excel formulas to extract insights from structured data (CSVs, Spreadsheets).
- Manually read and use "Ctrl+F" to hunt for specific clauses and context inside massive unstructured documents (100-page PDF financial reports).
- Constantly switch between different tools (database clients, PDF viewers, BI dashboards) depending on the type of data they are analyzing.

DataPilot solves this by acting as a unified, natural language analytical engine. It seamlessly handles both structured and unstructured data through a Hybrid Retrieval-Augmented Generation (RAG) architecture.

## 2. System Architecture: How It Works & Why

Our system is divided into Three Major Pillars.

### Pillar 1: Data Ingestion & Processing Engine (The Backend Pipeline)
Instead of forcing users to pre-process their data, the system automatically structures it upon upload.

**How it works:**
- **Routing:** When a file is uploaded to the FastAPI backend, the system identifies its type.
- **Structured Data Pipeline (SQLite + Pandas):** If it's a CSV, Excel, or JSON, Pandas reads the file, sanitizes the column names, and dynamically creates a new table in a local SQLite database (`datapilot.db`).
- **Unstructured Data Pipeline (FAISS + Langchain):** If it's a PDF or TXT, Langchain's loaders extract the raw text. A `RecursiveCharacterTextSplitter` chunks the text into digestible pieces. These chunks are embedded using Google Gemini Embeddings and stored in a local FAISS vector database.

**Why we did it this way:**
- **Dual Database Approach over Pure Vector DB:** While Vector Databases (like FAISS) are incredible for semantic similarity, they are terrible at exact math, aggregations, and filtering (e.g., "Sum the revenue where region = North"). By using SQLite for tables and FAISS for text, we get the best of both worlds.
- **Pandas for ETL:** Pandas is exceptionally fast at reading various tabular formats and handles missing data gracefully before pushing it to SQL.

### Pillar 2: The Hybrid AI Routing Engine (The Logic Layer)
When a user asks a question, they don't have to specify which file they are asking about. They just use natural language.

**How it works:**
- **Tool-Calling Agent:** We use Langchain to create an AI Agent powered by Google Gemini (1.5 Flash). 
- **Dynamic Tool Selection:** The agent is equipped with two specific tools: a `sql_query_tool` (which can execute SQL against SQLite) and a `knowledge_retrieval_tool` (which queries FAISS).
- **Execution:** When the user asks "What were Q1 sales?", the LLM realizes it needs exact numbers and writes a SQL query. If they ask "Summarize the risk factors in the report", it executes a semantic search against the vector store.

**Why we did it this way:**
- **LLM-Driven Routing over Brittle If/Else logic:** Instead of writing complex Regex or classification models to route the user's query, we give the LLM the tools and let it reason about the best approach.
- **Gemini 1.5 Flash:** It provides a massive context window and rapid response times, making the conversational experience feel instantaneous and reliable.

### Pillar 3: The Aesthetic User Interface (The Frontend)
A premium analytical tool must feel fast, intuitive, and beautiful.

**How it works:**
- **React + Vite:** We use React for a component-based chat architecture and Vite for lightning-fast build times.
- **Design System:** We implemented a modern, sleek dark-themed interface using Tailwind CSS and Lucide React icons, focusing on minimalism to let the data shine.
- **Micro-Interactions:** We utilize Framer Motion to animate message bubbles and loading states, providing satisfying visual feedback.

**Why we did it this way:**
- **Tailwind CSS:** Allows us to rapidly prototype and enforce strict design constraints, ensuring consistent spacing, colors, and typography across the entire application without leaving the JSX files.
- **Framer Motion:** Static chat interfaces feel dead. Adding subtle entry animations makes the AI feel like a responsive, living assistant.

## 3. Detailed User Workflow

Let's walk through the exact journey of a user, "Sarah," an analyst from the moment she opens DataPilot.

```mermaid
sequenceDiagram
    actor Sarah as Sarah (User)
    participant React as React Frontend
    participant Fast as FastAPI Backend
    participant Agent as Gemini Agent
    participant SQL as SQLite DB
    participant FAISS as FAISS Vector DB

    Sarah->>React: Uploads "Sales.csv" & "Q1_Report.pdf"
    React->>Fast: POST /upload (files)
    Fast->>SQL: Parse CSV via Pandas, Create Table
    Fast->>FAISS: Chunk PDF, Embed, Save to Vector Store
    Fast-->>React: Success Response
    
    Sarah->>React: Types "What is the total revenue and what are the main risks?"
    React->>Fast: POST /chat (message)
    Fast->>Agent: Invoke Agent with user message
    
    Note over Agent, FAISS: Agent determines tools needed
    
    Agent->>SQL: Executes SUM(revenue) query
    SQL-->>Agent: Returns structured result ($1.2M)
    
    Agent->>FAISS: Searches for "main risks"
    FAISS-->>Agent: Returns text chunks (Supply chain delays)
    
    Agent->>Fast: Synthesizes final natural language response
    Fast-->>React: JSON Response
    React-->>Sarah: Displays animated, formatted response
```

### Step 1: The Ingestion Phase
- **Uploading:** Sarah drags and drops both her `SalesData.csv` and `AnnualReport.pdf` into the sidebar.
- **The Magic:** Behind the scenes, the FastAPI server routes the CSV to the SQL database and the PDF to the FAISS vector store. The UI shows a subtle loading spinner, followed by the files appearing in her "Sources" list.

### Step 2: The Query Phase
- **Asking Questions:** Instead of writing SQL, she simply types: "Calculate the total profit for the enterprise tier and summarize the security concerns mentioned in the report."
- **Reasoning:** Within milliseconds, the Langchain Agent intercepts the query. It realizes it has a multi-part question. It uses the `sql_query_tool` to calculate the profit, and simultaneously uses the `knowledge_retrieval_tool` to pull security context from the PDF.

### Step 3: The Insight Phase
- **Displaying Results:** The frontend receives a synthesized, highly accurate response. Framer Motion smoothly animates the text onto the screen. Sarah gets both the exact financial numbers and the nuanced risk summary in one cohesive message, without ever opening Excel or a PDF viewer.

## 4. Why This Architecture Wins (The "AI Engineer" Perspective)

By building the system this way, we prove we aren't just building a standard chatbot. We are building an Intelligent Analytical System:

- **True Hybrid RAG:** We solve the biggest flaw of standard RAG architectures (which fail spectacularly at mathematical aggregations and counting) by integrating deterministic SQL tools alongside probabilistic semantic search.
- **Extensible:** Because we use an Agent-based architecture, adding a new data source (like a live Postgres database, Notion, or an API) is as simple as defining a new `@tool` in Python. The LLM will automatically learn how to use it.
- **Delightful:** We shifted the immense cognitive load from the user (writing formulas, reading manuals, filtering rows) to the machine (AI intent parsing and tool execution), creating a frictionless, premium analytical experience.

---

## 5. Tech Stack Reference — Full Breakdown

> This section documents every technology used in DataPilot, grouped by layer. It is also available as an interactive in-app page — click **"Tech Stack"** in the sidebar of the DataPilot UI to explore it visually with animations, hover effects, and architecture flow cards.

---

### Layer 1 — Frontend (React + Vite)

| Technology | Version | Category | Purpose |
|---|---|---|---|
| **React** | 19.2.5 | Core Framework | Declarative, component-based UI. Manages state, side-effects, and the entire chat interface |
| **Vite** | 8.0.10 | Build Tool | Instant Hot Module Replacement (HMR), sub-second builds, and ES module-native bundling |
| **TailwindCSS** | v4.2.4 | Styling | Utility-first CSS with `@theme` design tokens for dark mode, spacing, and color palette |
| **Framer Motion** | 12.38.0 | Animation | Declarative spring animations for message bubbles, loading states, and page transitions |
| **Lucide React** | 1.11.0 | Icon System | Consistent, crisp SVG icons (Send, Upload, Layers, FileText, FileSpreadsheet) |
| **Recharts** | 3.8.1 | Data Visualization | Composable charting library built on D3 for future chart rendering from query results |
| **Axios** | 1.15.2 | HTTP Client | Promise-based HTTP for `/upload` and `/chat` API calls with automatic error handling |
| **clsx + tailwind-merge** | Latest | Utility | Conditional className composition and Tailwind class conflict resolution |
| **@vitejs/plugin-react** | 6.0.1 | Vite Plugin | Fast Refresh and JSX transform for React 19 |
| **PostCSS + Autoprefixer** | 8.x / 10.x | CSS Build | Autoprefixes CSS vendor prefixes for cross-browser compatibility |

---

### Layer 2 — Backend (Python + FastAPI)

| Technology | Version | Category | Purpose |
|---|---|---|---|
| **FastAPI** | Latest | API Framework | High-performance async Python REST API. Exposes `POST /upload` and `POST /chat` endpoints |
| **Uvicorn** | Latest | ASGI Server | Lightning-fast async server that runs FastAPI in development |
| **Gunicorn** | Latest | WSGI Process Manager | Production-grade process manager. Spawns Uvicorn workers on Render via `Procfile` |
| **python-multipart** | Latest | Form Parsing | Enables FastAPI to receive multipart file uploads |
| **SQLAlchemy** | Latest | ORM / SQL Toolkit | Creates the DB engine, inspects schemas, and runs queries. Supports SQLite + PostgreSQL |
| **Pandas** | Latest | ETL / Data Manipulation | Reads CSV, Excel, JSON files and transforms them into SQL tables with sanitized column names |
| **openpyxl** | Latest | Excel Engine | Backend engine used by Pandas to read `.xls` and `.xlsx` Excel workbooks |
| **PyPDF** | Latest | PDF Parser | Pure-Python library to extract raw text from text-based PDF documents page by page |
| **python-dotenv** | Latest | Config Management | Loads `GOOGLE_API_KEY`, `GROQ_API_KEY`, and `DATABASE_URL` from `.env` files at startup |
| **psycopg2-binary** | Latest | PostgreSQL Adapter | Python driver for connecting SQLAlchemy to PostgreSQL in production |
| **pgvector** | Latest | PGVector Extension | PostgreSQL extension client library enabling vector similarity operations |

---

### Layer 3 — AI Engine (LangChain + LLM)

| Technology | Model / Version | Category | Purpose |
|---|---|---|---|
| **LangChain** | Latest | Agent Framework | Core orchestration — builds the tool-calling agent, manages prompts and agent executor |
| **LangChain-Groq** | Latest | LLM Provider | Integrates Groq's ultra-fast hosted inference for LLaMA 3.3-70B |
| **LangChain-Community** | Latest | Integrations | Provides loaders (`PyPDFLoader`, `TextLoader`), embeddings, and vector store wrappers |
| **LangChain-Google-GenAI** | Latest | Embedding Provider | Wraps Google's `GoogleGenerativeAIEmbeddings` for `gemini-embedding-001` |
| **LLaMA 3.3-70B Versatile** | via Groq | Reasoning LLM | The core language model that reads schemas, writes SQL, selects tools, and synthesizes answers |
| **Google Gemini Embeddings** | `gemini-embedding-001` | Vector Embeddings | Converts text chunks into high-dimensional vectors for semantic similarity search |
| **Sentence-Transformers** | `BAAI/bge-small-en-v1.5` | Local Fallback | HuggingFace embedding model used when `GOOGLE_API_KEY` is absent (dev-only) |
| **`create_tool_calling_agent`** | LangChain Classic | Agent Builder | Constructs a ReAct-style agent that binds the LLM to tool schemas |
| **`AgentExecutor`** | LangChain Classic | Execution Loop | Runs the agent loop: reason → act → observe → respond |
| **`RecursiveCharacterTextSplitter`** | LangChain | Chunking | Splits documents into 1,000-character chunks with 100-character overlap for optimal retrieval |

---

### Layer 4 — Databases & Vector Stores

| Technology | Type | Environment | Purpose |
|---|---|---|---|
| **PostgreSQL + PGVector** | Relational + Vector DB | Production (Render) | Primary database. Handles both structured SQL tables AND vector embeddings via the `pgvector` extension |
| **SQLite** | Relational DB | Local Development | Lightweight file-based SQL database (`datapilot.db`) for local structured data storage |
| **PGVector (LangChain)** | Vector Store | Production | `langchain_community.vectorstores.pgvector.PGVector` — stores and retrieves embedded document chunks |
| **FAISS (CPU)** | Vector Index | Local Fallback | `faiss-cpu` — Facebook AI Similarity Search, used in early dev iterations for in-memory vector indexing |

---

### Layer 5 — DevOps & Deployment

| Technology | Category | Purpose |
|---|---|---|
| **Render** | Cloud Platform | Hosts the FastAPI backend as a Web Service and the React app as a Static Site |
| **GitHub** | Version Control | Source of truth for the codebase. Render auto-deploys on push to `main` |
| **Procfile** | Process Declaration | Declares `web: gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app` for Render |
| **`.env` / Environment Variables** | Config | Stores `GOOGLE_API_KEY`, `GROQ_API_KEY`, `DATABASE_URL` securely outside the codebase |
| **`RENDER` env flag** | Guard Logic | `vector_store.py` checks `os.getenv("RENDER")` to block memory-heavy local fallbacks in production |

---

### Full Architecture — Component Map

```
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                              DataPilot — Full System Architecture                           ║
╠══════════════════════╦═══════════════════════════════════╦═══════════════════════════════════╣
║   FRONTEND (React)   ║       BACKEND (FastAPI)           ║   AI LAYER (LangChain + Groq)    ║
║                      ║                                   ║                                   ║
║  App.jsx             ║  main.py                          ║  agent.py                         ║
║  ┌─────────────┐     ║  ┌──────────┐  ┌──────────────┐  ║  ┌──────────────────────────┐    ║
║  │  Sidebar    │     ║  │ /upload  │  │   /chat      │  ║  │  LangChain AgentExecutor │    ║
║  │  - Sources  │     ║  └────┬─────┘  └──────┬───────┘  ║  │  + LLaMA 3.3-70B (Groq) │    ║
║  │  - TechStack│     ║       │                │          ║  └────────────┬─────────────┘    ║
║  └─────────────┘     ║       ▼                ▼          ║               │                  ║
║  ┌─────────────┐     ║  ┌────────┐     ┌──────────┐     ║    ┌──────────┴───────────┐      ║
║  │  Chat Area  │◄────╫──│ Router │     │ask_data  │◄────╫────│   Tool Selection     │      ║
║  │  Messages   │     ║  └───┬────┘     │   pilot()│     ║    └──────┬───────────────┘      ║
║  └─────────────┘     ║      │          └──────────┘     ║           │                      ║
║  TechStack.jsx        ║      ├── CSV/XLS/JSON            ║     ┌─────┴───────┐              ║
║  ┌─────────────┐     ║      │   └─► database.py         ║     │             │              ║
║  │ Architecture│     ║      │       Pandas → SQLAlchemy  ║  sql_query  knowledge_          ║
║  │ Flow Cards  │     ║      │                            ║   _tool     retrieval_tool       ║
║  │ Tech Tables │     ║      └── PDF/TXT                  ║     │             │              ║
║  └─────────────┘     ║          └─► vector_store.py      ║     ▼             ▼              ║
║                      ║              PyPDF → Chunk         ║  SQLite/    PGVector +           ║
║  Framer Motion       ║              → Embed → PGVector    ║  PostgreSQL Gemini Embed         ║
║  Axios HTTP          ║                                    ║                                  ║
╚══════════════════════╩═══════════════════════════════════╩═══════════════════════════════════╝
```

---

### Interactive Tech Stack Page

The Tech Stack page (`TechStack.jsx`) is built directly into the DataPilot UI and is accessible from the sidebar. It renders:

- **Architecture Flow** — 6 animated step cards walking through the full request lifecycle (Upload → Route → SQL Pipeline → Vector Pipeline → Agent → Answer)
- **5 Category Sections** — Frontend, Backend, AI & LLM, Databases, DevOps — each with colored glows and hover effects
- **Tech Cards** — Each technology is presented with its name, a color-coded category badge, and a one-line description
- **Sticky Header** with a "← Back to App" button to return to the chat interface without losing state

> **To access:** Click the `Tech Stack` button in the bottom-left sidebar of the DataPilot chat interface.

---

*Last updated: June 2026 · DataPilot v1.0 · Hybrid RAG Architecture*
