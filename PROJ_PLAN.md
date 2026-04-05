# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status | Completed |
|-------|-------|--------|-----------|
| Phase 1 | Environment & Scaffolding | ✅ COMPLETE | 2026-04-04 |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | ✅ COMPLETE | 2026-04-04 |
| Phase 3 | Language-Aware Code Chunking Engine | ✅ COMPLETE | 2026-04-04 |
| Phase 4 | Qdrant Vector DB Integration | ✅ COMPLETE | 2026-04-05 |
| Phase 5 | Embedding Generation (HuggingFace) | PENDING | — |
| Phase 6 | Groq LLM Integration & RAG Chain | PENDING | — |
| Phase 7 | Citation Extraction & Dependency Tracking | PENDING | — |
| Phase 8 | Frontend UI (Next.js App Router) | PENDING | — |
| Phase 9 | Deployment, Testing & Production Hardening | PENDING | — |

---

## Phase 4 Completion Checklist ✅ COMPLETE

- [x] `qdrant-client==1.7.0` installed
- [x] `models/vector_schemas.py` — ChunkMetadata, VectorChunk Pydantic models
- [x] `services/vector_db.py` — VectorDBClient with full API
  - [x] `create_collection_if_not_exists()` — creates cosine 384-dim collection
  - [x] `upsert_chunk()` — single point upsert
  - [x] `upsert_chunks_batch()` — batch upsert in 100-point batches
  - [x] `query()` — dense similarity search with optional metadata filter
  - [x] `delete_collection()` — cleanup
  - [x] `get_collection_stats()` — vector count, config
  - [x] Graceful degradation — all methods return safe defaults when unavailable
- [x] `config.py` updated — QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, VECTOR_DIMENSION
- [x] `models/schemas.py` updated — `chunks_indexed_in_db`, `vector_db_status` fields added
- [x] `services/ingestion.py` updated — upserts chunks to Qdrant after chunking
- [x] `routers/health.py` updated — shows `"qdrant": "connected" | "not_configured"`
- [x] `main.py` updated — initializes VectorDBClient at startup, injects into services
- [x] `tests/test_vector_db.py` — 8 unit tests using in-memory Qdrant (no API key needed)
- [x] `QDRANT_SETUP.md` — step-by-step Qdrant Cloud setup guide
- [x] `.env.example` updated with Qdrant vars
- [x] **20/20 tests pass** (12 chunking + 8 vector DB)

**Test results:**
- In-memory Qdrant used for tests (no API key required for CI)
- All batch upsert, query, metadata preservation tests pass
- Graceful degradation: unavailable client returns safe defaults

**Pending (needs user action):**
- QDRANT_URL and QDRANT_API_KEY secrets need to be set in Replit Secrets
- Once set, health endpoint shows `"qdrant": "connected"`
- Full ingestion test with real Qdrant Cloud (Phase 5 adds real embeddings)

---

## Vector DB Schema (Qdrant)

### Collection: `codemind-codebase`
| Field | Type | Description |
|-------|------|-------------|
| `vector` | float[384] | Dense embedding (placeholder zeros until Phase 5) |
| `distance` | cosine | Similarity metric |

### Payload (Metadata per chunk)
| Field | Type | Description |
|-------|------|-------------|
| `file_path` | str | Absolute path in cloned repo |
| `start_line` | int | 1-indexed start line |
| `end_line` | int | 1-indexed end line |
| `language` | str | python / javascript / typescript / java |
| `function_name` | str? | Extracted function/class name |
| `dependencies` | str[] | Import dependencies |
| `repo_name` | str | `owner/repo` |
| `code_snippet` | str | First 200 chars of chunk |
| `content` | str | Full chunk text |
| `char_count` | int | Length in characters |
| `token_count` | int | Approximate tokens |
| `timestamp` | str | ISO 8601 ingest time |

---

## Qdrant Setup Steps (for developers)

See `artifacts/codemind-rag/backend/QDRANT_SETUP.md` for full instructions.

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io) (free 1GB)
2. Create cluster → get URL + API key
3. Set `QDRANT_URL` and `QDRANT_API_KEY` in Replit Secrets
4. Collection `codemind-codebase` (384-dim, cosine) auto-created on first ingest

---

## Query Flow (Phase 5+)

```
User question
    ↓
Embed with all-MiniLM-L6-v2 → 384-dim vector  [Phase 5]
    ↓
Dense search: Qdrant cosine similarity, top-10  [Phase 5]
    ↓
Sparse search: BM25 keyword match, top-10       [Phase 5]
    ↓
Merge with RRF (k=60) → ranked top-10           [Phase 5]
    ↓
Format context → Groq llama-3.1-70b             [Phase 6]
    ↓
Extract citations → render in frontend          [Phase 7-8]
```

---

## API Contract

| Endpoint | Method | Status Code | Phase | Status |
|----------|--------|-------------|-------|--------|
| `/api/health` | GET | 200 | Phase 2 | ✅ Live (shows Qdrant status) |
| `/api/ingest` | POST | 202 | Phase 2 | ✅ Live |
| `/api/ingest/status/{job_id}` | GET | 200 / 404 | Phase 2 | ✅ Live |
| `/api/query` | POST | 200 | Phase 6 | Pending |
| `/api/dependencies` | GET | 200 | Phase 7 | Pending |

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
