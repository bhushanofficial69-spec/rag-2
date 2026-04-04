# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status | Completed |
|-------|-------|--------|-----------|
| Phase 1 | Environment & Scaffolding | ✅ COMPLETE | 2026-04-04 |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | ✅ COMPLETE | 2026-04-04 |
| Phase 3 | Language-Aware Code Chunking Engine | PENDING | — |
| Phase 4 | Embedding Generation & Qdrant Vector DB | PENDING | — |
| Phase 5 | Hybrid Search (Dense + BM25 + RRF) | PENDING | — |
| Phase 6 | Groq LLM Integration & RAG Chain | PENDING | — |
| Phase 7 | Citation Extraction & Dependency Tracking | PENDING | — |
| Phase 8 | Frontend UI (Next.js App Router) | PENDING | — |
| Phase 9 | Deployment, Testing & Production Hardening | PENDING | — |

---

## Phase 1 Completion Checklist ✅ COMPLETE

- [x] Next.js 14 (v14.2.35) project created with App Router
- [x] TypeScript strict mode enabled
- [x] Tailwind CSS v4 configured
- [x] All directories created: app/, components/ui/, lib/, types/, public/
- [x] Scaffold components created: ChatInterface, CodeViewer, FileTree, RepoInput
- [x] Shadcn/ui Button component (Radix UI + class-variance-authority)
- [x] lib/utils.ts, lib/api.ts, lib/constants.ts, types/index.ts
- [x] .env.example + README.md
- [x] Dev server verified: Next.js 14.2.35 on port 23968, HTTP 200

---

## Phase 2 Completion Checklist ✅ COMPLETE

- [x] FastAPI backend created at `artifacts/codemind-rag/backend/`
- [x] Python 3.11 runtime installed
- [x] All 10 packages installed (pinned versions)
- [x] `config.py` — Pydantic BaseSettings (GITHUB_TOKEN, MAX_REPO_SIZE, MAX_FILES, TEMP_DIR, LOG_LEVEL)
- [x] `models/schemas.py` — IngestRequest (with GitHub URL validation), IngestResponse, IngestionStatus, HealthResponse
- [x] `utils/logger.py` — structlog with ConsoleRenderer (dev) / JSONRenderer (prod)
- [x] `services/repo_cloner.py` — RepoCloner with GitPython, auth, 5-min timeout, error classification
- [x] `services/file_filter.py` — FileFilter with extension + directory exclusion + 100KB cap
- [x] `services/ingestion.py` — IngestionService with UUID job IDs, in-memory store, ThreadPoolExecutor
- [x] `routers/health.py` — GET /api/health returns 200 with service statuses + uptime
- [x] `routers/ingest.py` — POST /api/ingest (202), GET /api/ingest/status/{job_id} (200/404)
- [x] `routers/query.py` — stub router for Phase 6
- [x] `main.py` — FastAPI app with CORS for localhost + Replit dev domains
- [x] `Dockerfile` + `docker-compose.yml`
- [x] `.env.example` + `backend/README.md`
- [x] Workflow registered: `artifacts/codemind-rag: FastAPI Backend` on port 8000

**Verified endpoints:**
- `GET /api/health` → 200 ✓
- `POST /api/ingest` bad URL → 422 ✓
- `POST /api/ingest` valid GitHub URL → 202 with job_id ✓
- `GET /api/ingest/status/{job_id}` → 200 with IngestionStatus ✓
- `GET /api/ingest/status/nonexistent` → 404 ✓
- CORS preflight → `access-control-allow-origin: http://localhost:3000` ✓

---

## API Contract

| Endpoint | Method | Status Code | Phase | Status |
|----------|--------|-------------|-------|--------|
| `/api/health` | GET | 200 | Phase 2 | ✅ Live |
| `/api/ingest` | POST | 202 | Phase 2 | ✅ Live |
| `/api/ingest/status/{job_id}` | GET | 200 / 404 | Phase 2 | ✅ Live |
| `/api/query` | POST | 200 | Phase 6 | Pending |
| `/api/dependencies` | GET | 200 | Phase 7 | Pending |

---

## Job Tracking (In-Memory)

```python
job_store: Dict[str, IngestionStatus] = {}

# IngestionStatus fields:
# job_id: str (UUID4)
# status: "queued" | "processing" | "completed" | "failed"
# files_indexed: int
# chunks_created: int (Phase 3+)
# error: Optional[str]
# progress_percent: int (0-100)
```

Flow: queued (5%) → processing (30% post-clone, 50% post-filter) → per-file (50–95%) → completed (100%)

---

## Backend Directory Structure

```
artifacts/codemind-rag/backend/
├── main.py              ← FastAPI entry point, CORS config
├── config.py            ← Pydantic Settings (env vars)
├── requirements.txt     ← 10 pinned Python packages
├── Dockerfile
├── docker-compose.yml   ← Qdrant placeholder for Phase 4
├── .env.example
├── README.md
├── routers/
│   ├── health.py        ← GET /api/health
│   ├── ingest.py        ← POST /api/ingest + GET /api/ingest/status/{id}
│   └── query.py         ← stub (Phase 6)
├── services/
│   ├── repo_cloner.py   ← GitPython clone with auth + timeout
│   ├── file_filter.py   ← Extension + dir filter + size cap
│   └── ingestion.py     ← Orchestrator + job_store
├── models/
│   └── schemas.py       ← Pydantic v2 models
└── utils/
    └── logger.py        ← structlog setup
```

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
