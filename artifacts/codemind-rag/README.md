# CodeMind RAG — Intelligent Codebase Search Engine

Ask natural language questions about any GitHub repository and get instant, cited answers powered by Hybrid Search + Groq LLM.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 (App Router) + TypeScript strict mode |
| **Styling** | Tailwind CSS v4 |
| **UI Components** | Shadcn/ui (Radix UI primitives) |
| **Code Viewer** | Monaco Editor (VS Code engine) |
| **Backend** | FastAPI (Python 3.11+) |
| **Vector DB** | Qdrant Cloud |
| **LLM** | Groq llama-3.1-70b-versatile |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 |

## Setup

### Frontend

```bash
pnpm install
pnpm --filter @workspace/codemind-rag run dev
```

### Environment Variables

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_MAX_QUERY_LENGTH=500
```

### Backend (Phase 2+)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Environment & Scaffolding | ✅ Complete |
| 2 | GitHub Repo Cloning & Ingestion API | Pending |
| 3 | Language-Aware Code Chunking | Pending |
| 4 | Embedding & Qdrant Vector DB | Pending |
| 5 | Hybrid Search (Dense + BM25 + RRF) | Pending |
| 6 | Groq LLM Integration & RAG Chain | Pending |
| 7 | Citation Extraction & Dependency Tracking | Pending |
| 8 | Frontend UI (Full Implementation) | Pending |
| 9 | Deployment & Production Hardening | Pending |

## Architecture

```
User Question
    │
    ▼
Next.js 14 Frontend (App Router)
    │
    ▼ HTTPS REST API
FastAPI Backend (Python 3.11+)
    │
    ├─ Qdrant Cloud (Vector DB)
    │   ├─ Dense vectors: 384-dim cosine
    │   └─ Sparse vectors: BM25
    │
    └─ Groq Cloud (LLM)
        └─ llama-3.1-70b-versatile
```
