from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional


class SearchQuery(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[Dict[str, str]] = None
    repo_name: Optional[str] = None

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query cannot be empty")
        return v.strip()

    @field_validator("top_k")
    @classmethod
    def clamp_top_k(cls, v: int) -> int:
        return min(max(v, 1), 20)


class SearchResult(BaseModel):
    id: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    function_name: Optional[str] = None
    code_snippet: str
    content: str
    repo_name: Optional[str] = None
    semantic_score: float
    keyword_score: float
    hybrid_score: float
    rank: int


class HybridSearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    query_embedding_time_ms: int
    search_time_ms: int


class RepoContext(BaseModel):
    repo_name: str
    repo_url: str
    languages: List[str] = []
    file_count: int = 0
    chunk_count: int = 0
    indexed_at: str = ""
