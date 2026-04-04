# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status | Completed |
|-------|-------|--------|-----------|
| Phase 1 | Environment & Scaffolding | ✅ COMPLETE | 2026-04-04 |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | PENDING | — |
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
- [x] TypeScript strict mode enabled (tsconfig.json strict: true)
- [x] Tailwind CSS v4 configured (@tailwindcss/postcss)
- [x] All required directories created: app/, components/ui/, lib/, types/, public/
- [x] Scaffold components created: ChatInterface, CodeViewer, FileTree, RepoInput
- [x] Shadcn/ui Button component created (Radix UI + class-variance-authority)
- [x] lib/utils.ts (cn helper), lib/api.ts (axios client), lib/constants.ts
- [x] types/index.ts (TypeScript interfaces for all API contracts)
- [x] .env.example with all frontend environment variables
- [x] README.md with setup instructions and phases overview
- [x] Dev server verified running: Next.js 14.2.35 on port 23968
- [x] Home page returns HTTP 200
- [x] Backend connection status indicator on home page

**Tech Stack Confirmed:**
- Framework: Next.js 14.2.35 (App Router) ✓
- Language: TypeScript 5.9.3 (strict mode) ✓
- Styling: Tailwind CSS v4 ✓
- Component Library: Shadcn/ui (Radix UI primitives) ✓
- Code Editor: @monaco-editor/react (installed) ✓
- Syntax Highlighting: prismjs (installed) ✓
- HTTP Client: axios ✓

---

## Phase 2 Preview — GitHub Repo Cloning & Ingestion Pipeline

- Create FastAPI (Python 3.11+) backend at `artifacts/codemind-rag/backend/`
- Implement RepoCloner service (GitPython, GitHub URL validation)
- Implement FileFilter service (language detection, directory exclusion)
- Implement IngestionService orchestrator with background tasks
- Expose: POST /api/ingest, GET /api/ingest/status/{job_id}, GET /api/health
- In-memory job tracking with UUID job IDs
- CORS configured for frontend domain

---

## API Contract (to be updated each phase)

| Endpoint | Method | Status | Phase |
|----------|--------|--------|-------|
| `/api/health` | GET | Planned | Phase 2 |
| `/api/ingest` | POST | Planned | Phase 2 |
| `/api/ingest/status/{job_id}` | GET | Planned | Phase 2 |
| `/api/query` | POST | Planned | Phase 6 |
| `/api/dependencies` | GET | Planned | Phase 7 |

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
