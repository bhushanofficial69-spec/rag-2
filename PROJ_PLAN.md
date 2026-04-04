# CodeMind RAG — Project Plan

## Phase Status

| Phase | Title | Status |
|-------|-------|--------|
| Phase 1 | Environment & Scaffolding | ACTIVE |
| Phase 2 | GitHub Repo Cloning & Ingestion Pipeline | PENDING |
| Phase 3 | Code Chunking Engine | PENDING |
| Phase 4 | Embedding & Vector Database Integration | PENDING |
| Phase 5 | Hybrid Search (Semantic + Keyword) | PENDING |
| Phase 6 | Groq LLM Integration & RAG Chain | PENDING |
| Phase 7 | Frontend UI (Next.js App Router) | PENDING |
| Phase 8 | End-to-End Testing & Refinement | PENDING |
| Phase 9 | Deployment & Production Hardening | PENDING |

---

## Phase Details

### Phase 1 — Environment & Scaffolding [ACTIVE]
- Initialize Next.js project with App Router
- Configure Tailwind CSS
- Set up environment variable structure (.env.local)
- Install core dependencies: Groq SDK, Supabase client / Pinecone client
- Confirm app runs without errors

### Phase 2 — GitHub Repo Cloning & Ingestion Pipeline [PENDING]
- Accept a GitHub repo URL as input
- Clone the repo server-side (or via API)
- Walk the file tree and filter relevant source files
- Store raw file contents for chunking

### Phase 3 — Code Chunking Engine [PENDING]
- Split source files into semantic chunks (by function, class, or logical block)
- Attach metadata: file path, language, chunk index, repo name
- Prepare chunks for embedding

### Phase 4 — Embedding & Vector Database Integration [PENDING]
- Generate embeddings for each chunk using an embedding model
- Upsert embedded chunks into Supabase pgvector or Pinecone
- Confirm storage and retrieval round-trip

### Phase 5 — Hybrid Search (Semantic + Keyword) [PENDING]
- Implement semantic search (vector similarity / cosine distance)
- Implement keyword search (BM25 / full-text search via Supabase or Pinecone sparse vectors)
- Combine results with a reciprocal rank fusion or weighted merge strategy
- Return top-K ranked chunks for a given query

### Phase 6 — Groq LLM Integration & RAG Chain [PENDING]
- Connect Groq SDK with selected model (e.g., llama3-70b-8192)
- Build the RAG prompt: system context + retrieved chunks + user query
- Stream responses back to the client
- Handle token limits and chunk truncation gracefully

### Phase 7 — Frontend UI (Next.js App Router) [PENDING]
- Repo URL input form
- Ingestion progress indicator
- Chat interface with streaming answer display
- Code syntax highlighting for retrieved chunks
- Responsive layout with Tailwind CSS

### Phase 8 — End-to-End Testing & Refinement [PENDING]
- Test full pipeline: clone → chunk → embed → search → LLM answer
- Tune chunk size, overlap, and retrieval K
- Validate answer quality against known repos
- Fix bugs and edge cases

### Phase 9 — Deployment & Production Hardening [PENDING]
- Configure production environment variables
- Set up Supabase / Pinecone production instances
- Deploy to Vercel or Replit production
- Add rate limiting, error boundaries, and logging

---

## Rules of the Build

- One phase at a time — no skipping ahead
- Each phase ends with a running, error-free app
- Phase status is updated here at the end of every phase
- The main agent waits for a Master Prompt before beginning each new phase
