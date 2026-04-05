"""
HybridSearch — Phase 6

Combines:
  1. Semantic search  — EmbeddingGenerator + VectorDB cosine similarity
  2. Keyword search   — In-memory TF-IDF KeywordIndex
  3. RRF merging      — Reciprocal Rank Fusion (k=60)

Works entirely without external credentials (mock embeddings + in-memory Qdrant).
"""
import time
from typing import Dict, List, Optional, Tuple

from services.embeddings import EmbeddingGenerator
from services.vector_db import VectorDBClient
from services.keyword_index import KeywordIndex
from utils.logger import get_logger

logger = get_logger(__name__)

_RRF_K = 60
_DEFAULT_WEIGHTS = {"semantic": 0.6, "keyword": 0.4}


class HybridSearch:
    def __init__(
        self,
        vector_db: VectorDBClient,
        embedding_generator: EmbeddingGenerator,
        keyword_index: KeywordIndex,
    ):
        self.vector_db = vector_db
        self.embedding_generator = embedding_generator
        self.keyword_index = keyword_index

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> Tuple[List[Dict], float]:
        t0 = time.monotonic()
        query_vector = self.embedding_generator.generate_embedding(query)
        embed_ms = (time.monotonic() - t0) * 1000

        results = self.vector_db.query(
            vector=query_vector,
            top_k=top_k,
            filters=filters,
        )
        logger.debug(
            "semantic_search_complete",
            results=len(results),
            embed_ms=round(embed_ms, 1),
        )
        return results, embed_ms

    def keyword_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        results = self.keyword_index.search(query, top_k=top_k, filters=filters)
        logger.debug("keyword_search_complete", results=len(results))
        return results

    def reciprocal_rank_fusion(
        self,
        semantic_results: List[Dict],
        keyword_results: List[Dict],
        k: int = _RRF_K,
    ) -> List[Dict]:
        rrf: Dict[str, Dict] = {}

        for rank, result in enumerate(semantic_results, 1):
            rid = result["id"]
            score = 1.0 / (k + rank)
            if rid not in rrf:
                rrf[rid] = {
                    "result": result,
                    "rrf_score": 0.0,
                    "semantic_score": result.get("score", 0.0),
                    "keyword_score": 0.0,
                }
            rrf[rid]["rrf_score"] += score

        for rank, result in enumerate(keyword_results, 1):
            rid = result["id"]
            score = 1.0 / (k + rank)
            kw_score = result.get("score", 0.0)
            if rid not in rrf:
                rrf[rid] = {
                    "result": result,
                    "rrf_score": 0.0,
                    "semantic_score": 0.0,
                    "keyword_score": kw_score,
                }
            else:
                rrf[rid]["keyword_score"] = kw_score
            rrf[rid]["rrf_score"] += score

        merged = sorted(rrf.values(), key=lambda x: x["rrf_score"], reverse=True)
        return [
            {
                **item["result"],
                "semantic_score": item["semantic_score"],
                "keyword_score": item["keyword_score"],
                "hybrid_score": item["rrf_score"],
            }
            for item in merged
        ]

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> Tuple[List[Dict], int, int]:
        t0 = time.monotonic()

        semantic_results, embed_ms = self.semantic_search(query, top_k=top_k, filters=filters)

        kw_filters = filters.copy() if filters else None
        if kw_filters and "repo_name" in kw_filters:
            kw_filters = {"repo_name": kw_filters["repo_name"]}
        keyword_results = self.keyword_search(query, top_k=top_k, filters=kw_filters)

        merged = self.reciprocal_rank_fusion(
            semantic_results, keyword_results, k=_RRF_K
        )
        top_results = merged[:top_k]

        search_ms = int((time.monotonic() - t0) * 1000)
        logger.info(
            "hybrid_search_complete",
            query_len=len(query),
            semantic=len(semantic_results),
            keyword=len(keyword_results),
            merged=len(merged),
            returned=len(top_results),
            search_ms=search_ms,
        )
        return top_results, int(embed_ms), search_ms
