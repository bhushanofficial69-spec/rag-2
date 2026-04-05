# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status | Completed |
|-------|-------|--------|-----------|
| Phase 1 | Environment & Scaffolding | ✅ COMPLETE | 2026-04-04 |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | ✅ COMPLETE | 2026-04-04 |
| Phase 3 | Language-Aware Code Chunking Engine | ✅ COMPLETE | 2026-04-04 |
| Phase 4 | Qdrant Vector DB Integration | ✅ COMPLETE | 2026-04-05 |
| Phase 5 | Embedding Generation (HuggingFace + Local Mock) | ✅ COMPLETE | 2026-04-05 |
| Phase 6 | Hybrid Search + Groq LLM & RAG Chain | PENDING | — |
| Phase 7 | Citation Extraction & Dependency Tracking | PENDING | — |
| Phase 8 | Frontend UI (Next.js App Router) | PENDING | — |
| Phase 9 | Deployment, Testing & Production Hardening | PENDING | — |

---

## Phase 5 Completion Checklist ✅ COMPLETE

- [x] `utils/hashing.py` — SHA-256 text hashing helper
- [x] `services/embedding_cache.py` — LRU-style in-memory cache (max_size eviction, hit/miss tracking)
- [x] `services/embeddings.py` — EmbeddingGenerator class
  - [x] HuggingFace Inference API mode (when HUGGINGFACE_API_KEY is set)
  - [x] Local mock mode (always available — deterministic unit-normalised 384-dim vectors from SHA-256)
  - [x] `generate_embedding(text)` with cache-check and cache-set
  - [x] `generate_embeddings_batch(texts)` — batch of 16, cache-aware
  - [x] Retry logic: 3 attempts with exponential backoff on network errors
  - [x] Hard fail on 401 (invalid API key)
  - [x] `mode` property: `"huggingface_api"` | `"local_mock"`
  - [x] `cache_stats()` → hits, misses, hit_rate, api_calls, mode
- [x] `services/vector_db.py` upgraded
  - [x] In-memory Qdrant fallback (when no QDRANT_URL/API_KEY)
  - [x] Cloud mode when credentials provided
  - [x] `storage_mode` property: `"cloud"` | `"in-memory"`
  - [x] Graceful fallback to in-memory if Cloud connection fails
- [x] `services/ingestion.py` upgraded
  - [x] Batch embedding via `generate_embeddings_batch()` (16 per batch)
  - [x] Embedding stats tracked per job (generated, cache_hits, api_calls)
  - [x] All 178 chunks embed + upsert to in-memory Qdrant in <1s
- [x] `config.py` updated — HUGGINGFACE_API_KEY, EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, EMBEDDING_CACHE_SIZE, EMBEDDING_CACHE_TTL
- [x] `models/schemas.py` updated — `embeddings_generated`, `embedding_cache_hits`, `total_embedding_api_calls`, `embedding_mode`
- [x] `routers/health.py` updated — shows `"huggingface": "connected" | "local-mock" | "not_configured"`, `"qdrant": "cloud" | "in-memory"`
- [x] `main.py` updated — initializes EmbeddingCache + EmbeddingGenerator + injects into IngestionService
- [x] `tests/test_embeddings.py` — 16 unit tests (all pass)
- [x] `HF_SETUP.md` — HuggingFace setup guide
- [x] `requirements.txt` updated with huggingface-hub
- [x] `.env.example` updated with embedding vars
- [x] **36/36 tests pass** (12 chunking + 8 vector DB + 16 embeddings)

### Embedding Stats (psf/requests end-to-end test)
- Files: 35 | Chunks: 178 | Embeddings: 178 | Indexed: 178
- Time: < 1s total (mock mode, no API calls)
- Qdrant: in-memory | Embeddings: local-mock

---

## Local Development Mode (No API Keys Required)

All services run in local/mock mode with zero credentials:

| Service | Mode | Behaviour |
|---------|------|-----------|
| Qdrant | in-memory | Full upsert/query, data lost on restart |
| HuggingFace | local-mock | Deterministic SHA-256 384-dim unit vectors |
| Groq | disconnected | Added in Phase 6 |

Health endpoint shows:
```json
{
  "services": {
    "qdrant": "in-memory",
    "huggingface": "local-mock",
    "groq": "disconnected"
  }
}
```

**Upgrade to cloud:** Set `QDRANT_URL` + `QDRANT_API_KEY` → qdrant becomes `"cloud"`.
Set `HUGGINGFACE_API_KEY` → huggingface becomes `"connected"`.

---

## Embedding Stats

| Metric | Description |
|--------|-------------|
| `embeddings_generated` | Total chunks embedded this job |
| `embedding_cache_hits` | Chunks served from cache (duplicate content) |
| `total_embedding_api_calls` | HF API calls made (0 in mock mode) |
| `embedding_mode` | `local_mock` or `huggingface_api` |

Cache hit rate improves significantly for repos with repeated patterns.

---

## API Contract

| Endpoint | Method | Status Code | Phase | Status |
|----------|--------|-------------|-------|--------|
| `/api/health` | GET | 200 | Phase 2 | ✅ Live (qdrant + huggingface status) |
| `/api/ingest` | POST | 202 | Phase 2 | ✅ Live (now includes embedding stats) |
| `/api/ingest/status/{job_id}` | GET | 200 / 404 | Phase 2 | ✅ Live |
| `/api/query` | POST | 200 | Phase 6 | Pending |
| `/api/dependencies` | GET | 200 | Phase 7 | Pending |

---

## Phase 4 Completion Checklist ✅ COMPLETE

- [x] qdrant-client==1.7.0 installed
- [x] `models/vector_schemas.py` — ChunkMetadata, VectorChunk
- [x] `services/vector_db.py` — VectorDBClient (full CRUD + graceful degradation)
- [x] `config.py` — QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_NAME, VECTOR_DIMENSION
- [x] `models/schemas.py` — chunks_indexed_in_db, vector_db_status
- [x] `services/ingestion.py` — upserts to Qdrant after chunking
- [x] `routers/health.py` — qdrant connection status
- [x] `main.py` — VectorDBClient startup wiring
- [x] `tests/test_vector_db.py` — 8 unit tests
- [x] `QDRANT_SETUP.md` — setup guide

---

## Query Flow (Phase 6+)

```
User question
    ↓
Embed with EmbeddingGenerator → 384-dim vector     [Phase 5 ✅]
    ↓
Dense search: Qdrant cosine similarity, top-10      [Phase 6]
    ↓
(Optional) BM25 keyword match + RRF merge           [Phase 6]
    ↓
Format context → Groq llama-3.1-70b                 [Phase 6]
    ↓
Extract file citations → render in frontend         [Phase 7-8]
```

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
6. All services have local fallbacks (no credentials required for dev)
