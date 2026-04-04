# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status | Completed |
|-------|-------|--------|-----------|
| Phase 1 | Environment & Scaffolding | ✅ COMPLETE | 2026-04-04 |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | ✅ COMPLETE | 2026-04-04 |
| Phase 3 | Language-Aware Code Chunking Engine | ✅ COMPLETE | 2026-04-04 |
| Phase 4 | Embedding Generation & Qdrant Vector DB | PENDING | — |
| Phase 5 | Hybrid Search (Dense + BM25 + RRF) | PENDING | — |
| Phase 6 | Groq LLM Integration & RAG Chain | PENDING | — |
| Phase 7 | Citation Extraction & Dependency Tracking | PENDING | — |
| Phase 8 | Frontend UI (Next.js App Router) | PENDING | — |
| Phase 9 | Deployment, Testing & Production Hardening | PENDING | — |

---

## Phase 3 Completion Checklist ✅ COMPLETE

- [x] `services/chunking.py` — ChunkingService with 4 methods
- [x] `detect_language()` — extension-based, returns python/javascript/typescript/java/unknown
- [x] `get_language_separators()` — language-specific separator lists
- [x] `chunk_code()` — RecursiveCharacterTextSplitter + line number tracking + function extraction
- [x] `_get_line_numbers()` — sequential scan (not str.find) for accurate line tracking
- [x] `_extract_function_name()` — AST for Python, regex for JS/TS/Java
- [x] `services/language_parser.py` — LanguageParser with extract_dependencies()
- [x] Python: ast.parse() for Import/ImportFrom nodes
- [x] JavaScript/TypeScript: regex for import/require
- [x] Java: regex for import statements
- [x] `models/schemas.py` — CodeChunk model added, IngestionStatus extended
- [x] `services/ingestion.py` — integrated chunking + dependency extraction
- [x] `tests/test_chunking.py` — 12 unit tests written
- [x] **12/12 tests pass** (pytest in 1.66s)
- [x] tiktoken==0.5.2, langchain==0.1.0, langchain-community==0.0.10 installed
- [x] `requirements.txt` updated

**Manual test results (psf/requests):**
- Cloned in 1.3s
- 35 Python files found
- **178 chunks created** (target: >100 ✓)
- All `start_line >= 1` ✓
- All `end_line >= start_line` ✓
- All `token_count >= 100` ✓

---

## Chunking Strategy

### Separators Per Language

| Language | Separators (priority order) |
|----------|----------------------------|
| Python | `\nclass `, `\ndef `, `\nasync def `, `\n\n`, `\n`, `. `, ` ` |
| JavaScript | `\nfunction `, `\nconst `, `\nlet `, `\nvar `, `\nclass `, `\n\n`, `\n`, `. `, ` ` |
| TypeScript | Same as JS + `\ninterface `, `\ntype ` |
| Java | `\npublic class `, `\nprivate class `, `\nprotected class `, `\npublic static `, `\npublic `, `\n\n`, `\n` |
| Default | `\n\n`, `\n`, `. `, ` ` |

### Chunk Parameters
- Target: 512 tokens (~2048 chars with 4 chars/token estimate)
- Overlap: 50 tokens
- Minimum: 100 tokens (smaller chunks discarded)
- Token counting: tiktoken `cl100k_base`, fallback to `len(text) // 4`

### Line Number Tracking
Sequential scan algorithm: after placing each chunk, scan forward from the previous chunk's end line to find the next match. Avoids false matches on duplicate code.

---

## CodeChunk Schema

```python
class CodeChunk(BaseModel):
    file_path: str       # Absolute path to source file
    start_line: int      # 1-indexed start line in original file
    end_line: int        # 1-indexed end line (inclusive)
    language: str        # python | javascript | typescript | java | unknown
    content: str         # Raw chunk text
    function_name: Optional[str]  # Extracted function/class name if found
    dependencies: List[str]       # Import dependencies from the file
    char_count: int      # Length in characters
    token_count: int     # Approximate token count (tiktoken cl100k_base)
```

---

## IngestionStatus Schema (Updated)

```python
class IngestionStatus(BaseModel):
    job_id: str
    status: str          # queued | processing | completed | failed
    files_indexed: int
    chunks_created: int  # Total chunks across all files
    total_chunks: int    # Same as chunks_created (alias for clarity)
    error: Optional[str]
    progress_percent: int  # 0-100 (clone: 0-30, filter: 30-40, chunk: 40-100)
    chunks: List[CodeChunk] = []  # In-memory store (moved to Qdrant in Phase 4)
```

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

## Backend Directory Structure

```
artifacts/codemind-rag/backend/
├── main.py
├── config.py
├── requirements.txt     ← Now includes langchain, tiktoken
├── Dockerfile / docker-compose.yml
├── routers/
│   ├── health.py        ← GET /api/health
│   ├── ingest.py        ← POST /api/ingest + status
│   └── query.py         ← stub (Phase 6)
├── services/
│   ├── repo_cloner.py   ← GitPython clone
│   ├── file_filter.py   ← Extension + dir filter
│   ├── ingestion.py     ← Orchestrator (now includes chunking)
│   ├── chunking.py      ← NEW: ChunkingService
│   └── language_parser.py ← NEW: dependency extraction
├── models/
│   └── schemas.py       ← CodeChunk added, IngestionStatus extended
├── tests/
│   └── test_chunking.py ← 12 unit tests (12/12 pass)
└── utils/
    └── logger.py
```

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
