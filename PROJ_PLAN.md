# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status |
|-------|-------|--------|
| Phase 1 | Environment & Scaffolding | ACTIVE |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | PENDING |
| Phase 3 | Language-Aware Code Chunking Engine | PENDING |
| Phase 4 | Embedding Generation & Qdrant Vector DB | PENDING |
| Phase 5 | Hybrid Search (Dense + BM25 + RRF) | PENDING |
| Phase 6 | Groq LLM Integration & RAG Chain | PENDING |
| Phase 7 | Citation Extraction & Dependency Tracking | PENDING |
| Phase 8 | Frontend UI (Next.js App Router) | PENDING |
| Phase 9 | Deployment, Testing & Production Hardening | PENDING |

---

## Phase Details

### Phase 1 — Environment & Scaffolding [ACTIVE]
**Goal:** Project structure created, all tools installed, app runs without errors.
- Initialize Next.js 14 project with App Router and TypeScript
- Configure Tailwind CSS and Shadcn/ui components
- Set up FastAPI (Python 3.11+) backend project structure
- Configure environment variables (.env.local for frontend, .env for backend)
- Install core dependencies: Groq SDK, Qdrant client, sentence-transformers, LangChain
- Confirm both frontend and backend start without errors
- Create initial `/api/health` endpoint

**Acceptance:** App runs, health check returns 200, no TypeScript or Python errors.

---

### Phase 2 — GitHub Repo Cloning & Ingestion Pipeline [PENDING]
**Goal:** System can accept a GitHub URL, clone it, and extract source files.
- Accept public GitHub repo URLs (format: https://github.com/owner/repo)
- Support branch selection (main, develop)
- Clone repo to temporary server storage
- Walk file tree, filter by extension (.py, .js, .ts, .java)
- Exclude directories: node_modules, .git, __pycache__, dist, build, vendor
- Skip files >100KB; process max 5000 files
- Clean up temp files after processing
- Expose `/api/ingest` POST and `/api/ingest/status/{job_id}` GET endpoints
- Track and report ingestion progress (files indexed, chunks created)

**Acceptance:** Can ingest a 1000-file Python repo, progress endpoint updates correctly, temp files deleted on completion.

---

### Phase 3 — Language-Aware Code Chunking Engine [PENDING]
**Goal:** Source files are split into semantic, searchable chunks.
- Detect language from file extension
- Use language-specific separators:
  - Python: `\nclass `, `\ndef `
  - JavaScript/TypeScript: `\nfunction `, `\nconst `, `\nclass `
- Target chunk size: 512 tokens with 50-token overlap
- Preserve complete function/class definitions (no mid-function splits)
- Extract: start_line, end_line, function_name per chunk
- Skip chunks <100 tokens
- Handle edge cases: multi-line strings, comments, decorators

**Acceptance:** No function split mid-definition; line numbers accurate ±1; average chunk 400-512 tokens; function names extracted for 95%+ of Python functions.

---

### Phase 4 — Embedding Generation & Qdrant Vector DB [PENDING]
**Goal:** Chunks are embedded and stored in Qdrant Cloud with full metadata.
- Use `sentence-transformers/all-MiniLM-L6-v2` model (384-dim dense vectors)
- Batch process chunks (16 per batch for efficiency)
- Cache embeddings to avoid regeneration
- Handle HuggingFace API rate limits (retry with exponential backoff)
- Create Qdrant collection with dense vectors (384 dims, COSINE distance)
- Create sparse BM25 vectors with IDF modifier
- Store payload: file_path, start_line, end_line, language, function_name, code_content, dependencies
- Support upsert (update existing chunks)
- Monitor collection size (warn at 80% of 1GB free limit)

**Acceptance:** 1500+ chunks stored in Qdrant with metadata; embeddings are exactly 384 dims; duplicate chunks use cached embeddings.

---

### Phase 5 — Hybrid Search (Dense + BM25 + RRF) [PENDING]
**Goal:** Search returns the most relevant chunks using combined vector + keyword approach.
- Embed user question via same model (384-dim)
- Execute dense vector search → top-10 results (cosine similarity)
- Execute sparse BM25 keyword search → top-10 results
- Merge results using Reciprocal Rank Fusion (RRF, k=60)
- Return top-10 ranked chunks with RRF score and confidence
- Query latency target: <1 second
- Handle empty result sets gracefully
- Expose search as internal service (used by RAG chain)

**Acceptance:** Hybrid outperforms dense-only on exact terms (e.g., "Error 503") and sparse-only on synonyms (e.g., "login" vs "authentication"); latency <1 second on 1500-chunk collection.

---

### Phase 6 — Groq LLM Integration & RAG Chain [PENDING]
**Goal:** Retrieved chunks are sent to Groq to generate cited, grounded answers.
- Format top-10 chunks as readable markdown context
- Build strict prompt template:
  - System: enforce citations, no hallucinations, 300-word limit
  - Context: retrieved code chunks with file paths and line numbers
  - User: natural language question
- Use Groq `llama-3.1-70b-versatile`, temperature 0.3
- Include code snippets (max 10 lines each) in answer
- Implement streaming response back to client
- Retry failed LLM calls up to 3 times
- Timeout: 30 seconds per request
- Expose `/api/query` POST endpoint

**Acceptance:** 95%+ of answers include valid file citations; no hallucinated functions; code snippets copy-paste accurate from source; LLM errors logged.

---

### Phase 7 — Citation Extraction & Dependency Tracking [PENDING]
**Goal:** Answers include validated citations and dependency impact warnings.
- Extract file paths from LLM response using regex (`/path/to/file.py`)
- Extract line ranges (`lines 45-78` or `line 45`)
- Validate citations against retrieved chunks
- Calculate confidence score (% of answer text that is cited)
- Parse Python imports (`import x`, `from x import y`)
- Parse JavaScript imports (`import x from 'y'`, `require('z')`)
- Build dependency graph during ingestion
- Store dependencies in chunk metadata
- Support transitive dependency resolution (A→B→C)
- Expose `/api/dependencies` GET endpoint

**Acceptance:** 90%+ citations valid; line numbers accurate ±1; dependency endpoint returns results in <1 second.

---

### Phase 8 — Frontend UI (Next.js App Router) [PENDING]
**Goal:** Full, working chat UI with code viewer, ingestion form, and responsive design.
- GitHub URL input form with validation and branch selector
- Ingestion progress bar with file count and estimated time remaining
- Cancel ingestion button
- Chat interface: question input (max 500 chars), message history
- Streaming answer display with markdown rendering
- Syntax-highlighted code snippets (Prism.js)
- Clickable file path links → open Monaco Editor code viewer
- Code viewer: read-only Monaco Editor, line numbers, Python/JS/TS/Java highlighting
- File tree navigation panel
- Copy-to-clipboard for code blocks
- Clear chat history button
- Responsive layout (mobile, tablet, desktop)
- Loading indicators and error messages throughout
- WCAG 2.1 AA accessibility (keyboard nav, ARIA labels)

**Acceptance:** End-to-end flow works: ingest repo → ask question → see answer → click file → view code. Works on mobile (iPhone 12+). Tab/Enter/Escape keyboard navigation functional.

---

### Phase 9 — Deployment, Testing & Production Hardening [PENDING]
**Goal:** System deployed, tested, documented, and demo-ready.
- Deploy FastAPI backend to Render (free tier)
- Deploy Next.js frontend to Vercel
- Configure GitHub Actions CI/CD pipeline
- Set all production environment variables securely
- Set up UptimeRobot pings (every 10 min to prevent Render cold starts)
- Test full pipeline end-to-end with 3 different repos (Python, JS, mixed)
- Test with 50+ sample questions, validate citation accuracy >90%
- Test with 5000-file repo (largest scale)
- Write README with architecture diagram + setup instructions + API docs (curl examples)
- Add rate limiting and request queuing (Groq 30 req/min limit)
- Verify all API endpoints return correct HTTP status codes
- Record 3-minute demo video

**Acceptance:** Backend health check live on Render; frontend live on Vercel; can index 5K-file repo; query latency p95 <4 seconds; README complete; demo video recorded.

---

## Rules of the Build

1. One phase at a time — no code written ahead of its phase prompt
2. Every phase ends with a running, error-free application
3. Phase status in this file is updated at the end of every phase
4. The main agent waits for a Master Prompt before beginning each phase
5. All secrets stored in environment variables — never in code
