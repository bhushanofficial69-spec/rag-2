# CodeMind RAG — Architecture

## Overview

CodeMind RAG is a "Google for Code" — a web-based Retrieval-Augmented Generation (RAG) system that allows developers to ask natural language questions about their codebase and receive cited, grounded answers with exact file references and code snippets.

---

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│   Next.js 14 (App Router) + TypeScript + Tailwind CSS            │
│                                                                  │
│  ┌─────────────────────┐    ┌────────────────────────────────┐   │
│  │  Chat Interface      │    │  Code Viewer (Monaco Editor)   │   │
│  │  - Question Input    │    │  - Syntax Highlighting         │   │
│  │  - Answer Streaming  │    │  - File Path + Line Numbers    │   │
│  │  - Citations         │    │  - Python, JS, TS, Java        │   │
│  └─────────────────────┘    └────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │  Repo Ingestion Form                                     │     │
│  │  - GitHub URL Input + Branch Selector + Progress Bar     │     │
│  └──────────────────────────────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS (REST API)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND — FastAPI (Python 3.11+)             │
│                     Hosted on: Render (free tier)                │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  API Endpoints                                          │     │
│  │  POST /api/ingest              → Start ingestion job    │     │
│  │  GET  /api/ingest/status/{id}  → Poll ingestion status  │     │
│  │  POST /api/query               → Ask question           │     │
│  │  GET  /api/dependencies        → Dependency analysis    │     │
│  │  GET  /api/health              → Health check           │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐      │
│  │  Ingestion   │  │  Chunking    │  │  RAG Chain         │      │
│  │  Pipeline    │  │  Engine      │  │  Orchestrator      │      │
│  │              │  │              │  │                    │      │
│  │  - Git Clone │  │  - 512 tok   │  │  - Embed query     │      │
│  │  - File Walk │  │  - 50 overlap│  │  - Hybrid search   │      │
│  │  - Filter    │  │  - Lang-aware│  │  - Format context  │      │
│  │  - Clean up  │  │  - Line nums │  │  - Call Groq LLM   │      │
│  └──────────────┘  └──────────────┘  └────────────────────┘      │
└──────────┬───────────────────────────────────┬───────────────────┘
           │                                   │
           ▼                                   ▼
┌──────────────────────┐           ┌───────────────────────────────┐
│  Qdrant Cloud        │           │  Groq Cloud                   │
│  (Vector Database)   │           │  (LLM Inference)              │
│                      │           │                               │
│  Dense Vectors:      │           │  Model: llama-3.1-70b-        │
│  384-dim (cosine)    │           │         versatile             │
│                      │           │  Temperature: 0.3             │
│  Sparse Vectors:     │           │  Max output: 300 words        │
│  BM25 weights        │           │  Timeout: 30 seconds          │
│                      │           │  Retry: up to 3x              │
│  Hybrid Search:      │           │                               │
│  RRF (k=60), top-10  │           │  Rate limit: 30 req/min       │
│                      │           │  (queue requests if exceeded) │
│  Free: 1GB storage   │           │  Free tier                    │
│  (~15K chunks)       │           │                               │
└──────────────────────┘           └───────────────────────────────┘
           │
           ▼
┌──────────────────────┐
│  HuggingFace         │
│  Inference API       │
│                      │
│  Model:              │
│  sentence-           │
│  transformers/       │
│  all-MiniLM-L6-v2   │
│                      │
│  384-dim embeddings  │
│  Batch size: 16      │
│  Cache enabled       │
│  Free tier           │
└──────────────────────┘
```

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 (App Router) | React framework with SSR/SSG |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Utility-first styling |
| Shadcn/ui | Latest | Accessible UI components |
| Monaco Editor | Latest | VS Code-grade code viewer (read-only) |
| Prism.js | Latest | Syntax highlighting (Python, JS, TS, Java) |
| **Hosting** | Vercel | Free tier, unlimited deployments |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | Python 3.11+ | Async REST API framework |
| AsyncIO | Built-in | Async background task processing |
| GitPython | Latest | Clone GitHub repositories |
| LangChain / LlamaIndex | Latest | RAG pipeline orchestration |
| **Hosting** | Render | Free tier (750 hrs/month) |

### AI / ML
| Technology | Purpose | Details |
|------------|---------|---------|
| sentence-transformers/all-MiniLM-L6-v2 | Embedding model | 384-dim dense vectors, via HuggingFace API |
| Qdrant Cloud | Vector database | Dense + sparse vectors, COSINE distance, BM25, free 1GB |
| Groq Cloud | LLM inference | llama-3.1-70b-versatile, temperature 0.3, 30 req/min |

### DevOps
| Technology | Purpose |
|------------|---------|
| GitHub | Version control |
| GitHub Actions | CI/CD pipeline |
| Docker | Containerization (backend) |
| Better Stack | Logging + monitoring (free tier) |
| UptimeRobot | Ping Render every 10 min (prevent cold starts) |

---

## RAG Pipeline (Step-by-Step)

```
1. INGESTION
   User submits GitHub URL + branch
   → Backend clones repo to /tmp
   → Walk file tree: filter .py .js .ts .java
   → Skip: node_modules, .git, __pycache__, dist, build, vendor
   → Skip files > 100KB, max 5000 files

2. CHUNKING
   For each source file:
   → Detect language from extension
   → Split using language-aware separators (functions, classes)
   → Target: 512 tokens, 50-token overlap
   → Extract: start_line, end_line, function_name
   → Skip chunks < 100 tokens

3. EMBEDDING
   For each chunk:
   → Call HuggingFace all-MiniLM-L6-v2 in batches of 16
   → Generate 384-dim dense vector
   → Compute BM25 sparse weights
   → Cache to avoid duplicate API calls

4. STORAGE (Qdrant)
   → Upsert chunk with dense vector (384-dim, COSINE)
   → Upsert sparse BM25 vector
   → Store payload: file_path, start_line, end_line, language,
                    function_name, code_content, dependencies

5. QUERY (Hybrid Search)
   User asks question
   → Embed question → 384-dim vector
   → Dense search: top-10 by cosine similarity
   → Sparse search: top-10 by BM25 keyword match
   → Merge with Reciprocal Rank Fusion (RRF, k=60)
   → Return top-10 ranked chunks with RRF scores

6. GENERATION (Groq LLM)
   → Format top-10 chunks as markdown context
   → Build strict prompt: enforce citations, no hallucinations
   → Call Groq llama-3.1-70b-versatile (temp=0.3, timeout=30s)
   → Stream answer back to frontend

7. CITATION & DISPLAY
   → Extract file paths + line numbers from LLM response (regex)
   → Validate citations against retrieved chunks
   → Calculate confidence score
   → Render: answer text + code snippets + clickable file links
   → Monaco Editor opens on file path click
```

---

## API Contract

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/health` | GET | — | `{ status: "ok" }` |
| `/api/ingest` | POST | `{ repo_url, branch }` | `{ job_id, status: "started" }` |
| `/api/ingest/status/{job_id}` | GET | — | `{ status, files_indexed, chunks_created, progress_pct }` |
| `/api/query` | POST | `{ question, repo_name, top_k }` | `{ answer, sources[], confidence_score, query_time_ms }` |
| `/api/dependencies` | GET | `?function=validate_user&repo=...` | `{ dependencies[], transitive[] }` |

---

## Data Model — Code Chunk (Qdrant Payload)

```json
{
  "id": "uuid",
  "file_path": "src/auth/login.py",
  "start_line": 45,
  "end_line": 78,
  "language": "python",
  "function_name": "validate_user",
  "code_content": "def validate_user(username, password):\n    ...",
  "repo_name": "owner/repo",
  "dependencies": ["src/api/users.py", "src/middleware/auth.py"],
  "external_dependencies": ["bcrypt", "sqlalchemy"],
  "chunk_size_tokens": 512,
  "vector_dense": [/* 384 floats */],
  "vector_sparse": { "validate": 1.8, "user": 1.2 }
}
```

---

## Environment Variables

### Backend (.env)
```
QDRANT_URL=https://your-cluster.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key
GROQ_API_KEY=your-groq-api-key
HUGGINGFACE_API_KEY=your-hf-token
GITHUB_TOKEN=your-github-token (optional, increases rate limit)
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
NEXT_PUBLIC_MAX_QUERY_LENGTH=500
```

---

## Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| LLM | Groq llama-3.1-70b-versatile | Fast inference, free tier, strong coding ability |
| Vector DB | Qdrant Cloud | Supports both dense + sparse natively, free 1GB |
| Embedding model | all-MiniLM-L6-v2 | 384-dim, fast, code-aware, free via HuggingFace |
| Search strategy | Hybrid (Dense + BM25 + RRF) | Best of both worlds: semantic + exact term matching |
| Chunking | Language-aware, 512 tok / 50 overlap | Preserves function context, reduces split artifacts |
| Frontend | Next.js App Router | SSR + streaming, Vercel deployment, TypeScript |
| Temperature | 0.3 | Deterministic, grounded answers, reduces hallucination |
| Strict prompt | Enforced citations | Prevents hallucination, increases trust in answers |
