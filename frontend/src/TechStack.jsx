import React from 'react';
import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: 'easeOut' },
  }),
};

const STACK = [
  {
    category: 'Frontend',
    color: '#38bdf8',
    glow: 'rgba(56,189,248,0.15)',
    items: [
      { name: 'React 19', desc: 'UI component library — declarative, reactive views', badge: 'Core' },
      { name: 'Vite 8', desc: 'Next-gen frontend build tool with instant HMR', badge: 'Build' },
      { name: 'TailwindCSS v4', desc: 'Utility-first styling with PostCSS integration', badge: 'Styling' },
      { name: 'Framer Motion', desc: 'Production-ready animations and layout transitions', badge: 'Anim' },
      { name: 'Lucide React', desc: 'Crisp, consistent icon system for React apps', badge: 'Icons' },
      { name: 'Recharts', desc: 'Composable charting library built on D3', badge: 'Charts' },
      { name: 'Axios', desc: 'Promise-based HTTP client for API communication', badge: 'HTTP' },
    ],
  },
  {
    category: 'Backend',
    color: '#34d399',
    glow: 'rgba(52,211,153,0.15)',
    items: [
      { name: 'FastAPI', desc: 'High-performance async Python web framework', badge: 'Core' },
      { name: 'Uvicorn / Gunicorn', desc: 'ASGI + WSGI server for production deployment', badge: 'Server' },
      { name: 'SQLAlchemy', desc: 'Python SQL toolkit and ORM', badge: 'ORM' },
      { name: 'Pandas', desc: 'Data manipulation and ETL for CSV / Excel / JSON', badge: 'ETL' },
      { name: 'openpyxl', desc: 'Excel file reader/writer engine for Pandas', badge: 'Excel' },
      { name: 'PyPDF', desc: 'Pure-Python PDF text extraction library', badge: 'PDF' },
      { name: 'python-dotenv', desc: 'Environment variable management via .env files', badge: 'Config' },
      { name: 'psycopg2-binary', desc: 'PostgreSQL adapter for Python', badge: 'DB' },
    ],
  },
  {
    category: 'AI & LLM',
    color: '#a78bfa',
    glow: 'rgba(167,139,250,0.15)',
    items: [
      { name: 'LangChain', desc: 'Framework for building LLM-powered applications', badge: 'Core' },
      { name: 'LangChain-Groq', desc: 'Groq-hosted LLaMA 3.3-70B ultra-fast inference', badge: 'LLM' },
      { name: 'LangChain-Community', desc: 'Community integrations: loaders, retrievers, stores', badge: 'Integr.' },
      { name: 'Google Gemini Embeddings', desc: 'gemini-embedding-001 for semantic vector search', badge: 'Embed' },
      { name: 'Sentence-Transformers', desc: 'Local BAAI/bge-small-en-v1.5 fallback embeddings', badge: 'Fallback' },
      { name: 'LLaMA 3.3-70B Versatile', desc: 'Groq-hosted open-source LLM for agent reasoning', badge: 'Model' },
    ],
  },
  {
    category: 'Databases & Storage',
    color: '#fb923c',
    glow: 'rgba(251,146,60,0.15)',
    items: [
      { name: 'PostgreSQL + PGVector', desc: 'Production vector store for semantic similarity search', badge: 'Vector DB' },
      { name: 'SQLite', desc: 'Lightweight local SQL database for structured data', badge: 'Structured' },
      { name: 'FAISS (CPU)', desc: 'Facebook AI Similarity Search — local vector indexing', badge: 'Local' },
    ],
  },
  {
    category: 'DevOps & Deployment',
    color: '#f472b6',
    glow: 'rgba(244,114,182,0.15)',
    items: [
      { name: 'Render', desc: 'Cloud platform for backend (Web Service) & frontend (Static)', badge: 'Hosting' },
      { name: 'GitHub', desc: 'Version control and CI/CD source of truth', badge: 'VCS' },
      { name: 'Procfile', desc: 'Gunicorn process declaration for Render deployment', badge: 'Config' },
    ],
  },
];

const ARCH_STEPS = [
  {
    step: '01',
    title: 'File Upload',
    desc: 'User uploads a CSV, Excel, JSON, PDF, or TXT file via the React UI. The file is sent to the FastAPI /upload endpoint.',
    color: '#38bdf8',
  },
  {
    step: '02',
    title: 'Smart Routing',
    desc: 'FastAPI detects the file type. Structured files (CSV/Excel/JSON) go to the SQL pipeline. Unstructured files (PDF/TXT) go to the Vector pipeline.',
    color: '#34d399',
  },
  {
    step: '03',
    title: 'SQL Pipeline',
    desc: 'Pandas reads the file → SQLAlchemy writes it as a table in PostgreSQL/SQLite. Schema is auto-detected for the LLM.',
    color: '#fb923c',
  },
  {
    step: '04',
    title: 'Vector Pipeline',
    desc: 'PyPDF/TextLoader extracts text → RecursiveCharacterTextSplitter chunks it → Gemini/BAAI Embeddings vectorize → PGVector stores.',
    color: '#a78bfa',
  },
  {
    step: '05',
    title: 'Hybrid Agent',
    desc: 'LangChain Agent (LLaMA 3.3-70B via Groq) dynamically selects between sql_query_tool and knowledge_retrieval_tool based on the question.',
    color: '#f472b6',
  },
  {
    step: '06',
    title: 'Answer Delivery',
    desc: 'The agent synthesizes an answer and returns it to the React UI via the /chat endpoint, displayed in the conversational interface.',
    color: '#fbbf24',
  },
];

export default function TechStack({ onBack }) {
  return (
    <div className="min-h-screen bg-background text-neutral-300 font-sans overflow-x-hidden">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl"
      >
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-white font-semibold tracking-tight text-lg">DataPilot</span>
            <span className="text-[10px] text-muted uppercase tracking-[0.2em] border border-border px-2 py-0.5 rounded-full">Tech Stack</span>
          </div>
          <button
            onClick={onBack}
            className="text-xs text-neutral-500 hover:text-neutral-200 transition-colors border border-border px-4 py-2 rounded-lg hover:bg-white/5"
          >
            ← Back to App
          </button>
        </div>
      </motion.header>

      <div className="max-w-6xl mx-auto px-6 py-20">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-24"
        >
          <div className="inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-muted border border-border px-4 py-2 rounded-full mb-8">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Architecture & Tech Stack
          </div>
          <h1 className="text-5xl font-bold text-white tracking-tight mb-6">
            Built for{' '}
            <span className="bg-gradient-to-r from-sky-400 via-violet-400 to-emerald-400 bg-clip-text text-transparent">
              Intelligence
            </span>
          </h1>
          <p className="text-neutral-400 text-lg max-w-2xl mx-auto leading-relaxed">
            DataPilot is a full-stack, production-grade Hybrid RAG application — combining a SQL agent and a vector search engine into one seamless data analyst.
          </p>
        </motion.div>

        {/* Architecture Flow */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-28"
        >
          <h2 className="text-xs uppercase tracking-[0.3em] text-muted mb-10 text-center">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ARCH_STEPS.map((step, i) => (
              <motion.div
                key={step.step}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                className="relative border border-border rounded-xl p-6 bg-surface/30 hover:bg-surface/60 transition-all duration-300 group overflow-hidden"
                style={{ '--glow': step.color }}
              >
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl"
                  style={{ background: `radial-gradient(circle at top left, ${step.color}18 0%, transparent 60%)` }}
                />
                <div className="relative z-10">
                  <span className="text-[11px] font-mono font-bold tracking-widest" style={{ color: step.color }}>
                    {step.step}
                  </span>
                  <h3 className="text-white font-semibold mt-2 mb-3">{step.title}</h3>
                  <p className="text-neutral-500 text-sm leading-relaxed">{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Tech Stack Grid */}
        {STACK.map((section, si) => (
          <motion.section
            key={section.category}
            custom={si}
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            className="mb-20"
          >
            <div className="flex items-center gap-4 mb-8">
              <div>
                <h2 className="text-white font-semibold text-lg">{section.category}</h2>
              </div>
              <div
                className="h-px flex-1 ml-4 opacity-30"
                style={{ background: `linear-gradient(to right, ${section.color}, transparent)` }}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {section.items.map((item, i) => (
                <motion.div
                  key={item.name}
                  custom={si * 5 + i}
                  variants={fadeUp}
                  initial="hidden"
                  animate="visible"
                  className="group border border-border rounded-xl p-5 bg-surface/20 hover:bg-surface/50 transition-all duration-300 relative overflow-hidden cursor-default"
                >
                  <div
                    className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{ background: `radial-gradient(circle at top left, ${section.glow} 0%, transparent 70%)` }}
                  />
                  <div className="relative z-10">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className="text-white font-medium text-sm">{item.name}</span>
                      <span
                        className="text-[9px] uppercase tracking-widest px-2 py-0.5 rounded-full border flex-shrink-0"
                        style={{ color: section.color, borderColor: `${section.color}40`, background: `${section.color}12` }}
                      >
                        {item.badge}
                      </span>
                    </div>
                    <p className="text-neutral-500 text-xs leading-relaxed">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>
        ))}

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center border-t border-border pt-12"
        >
          <p className="text-[11px] text-muted uppercase tracking-[0.3em]">
            DataPilot — Hybrid RAG Architecture
          </p>
          <p className="text-[10px] text-neutral-700 mt-2">
            FastAPI · LangChain · Groq · PGVector · React · Vite
          </p>
        </motion.div>
      </div>
    </div>
  );
}
