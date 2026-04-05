const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface IngestRequest {
  repo_url: string;
  branch?: string;
}

export interface IngestResponse {
  status: string;
  job_id: string;
  message: string;
}

export interface IngestionStatus {
  job_id: string;
  status: string;
  files_indexed: number;
  chunks_created: number;
  total_chunks: number;
  chunks_indexed_in_db: number;
  vector_db_status: string;
  embeddings_generated: number;
  embedding_cache_hits: number;
  total_embedding_api_calls: number;
  embedding_mode: string;
  error?: string | null;
  progress_percent: number;
}

export interface SearchResult {
  id: string;
  file_path: string;
  start_line: number;
  end_line: number;
  language: string;
  function_name?: string | null;
  code_snippet: string;
  content: string;
  repo_name?: string | null;
  semantic_score: number;
  keyword_score: number;
  hybrid_score: number;
  rank: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  query_embedding_time_ms: number;
  search_time_ms: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  services: Record<string, string>;
  uptime_seconds: number;
}

export interface IndexedRepo {
  repo_name: string;
  repo_url: string;
  languages: string[];
  file_count: number;
  chunk_count: number;
  indexed_at: string;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  health(): Promise<HealthResponse> {
    return request("GET", "/api/health");
  },

  ingest(repo_url: string, branch = "main"): Promise<IngestResponse> {
    return request("POST", "/api/ingest", { repo_url, branch });
  },

  getStatus(job_id: string): Promise<IngestionStatus> {
    return request("GET", `/api/ingest/status/${job_id}`);
  },

  search(
    query: string,
    repo_name?: string,
    top_k = 10,
    filters?: Record<string, string>
  ): Promise<SearchResponse> {
    return request("POST", "/api/search", {
      query,
      repo_name,
      top_k,
      filters,
    });
  },

  listRepos(): Promise<{ repos: IndexedRepo[] }> {
    return request("GET", "/api/search/repos");
  },
};
