"""
VectorDBClient — wraps Qdrant (Cloud or in-memory).

Priority:
  1. Qdrant Cloud  — when QDRANT_URL + QDRANT_API_KEY are set
  2. In-memory     — always available, zero config, perfect for local dev

In-memory Qdrant is fully functional (upsert, query, delete) but does NOT
persist data between restarts.  It's the development fallback until Cloud
credentials are supplied.
"""

import uuid
from typing import Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from utils.logger import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 100


class VectorDBClient:
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "codemind-codebase",
        dimension: int = 384,
    ):
        self.collection_name = collection_name
        self.dimension = dimension
        self._cloud_mode = bool(url and api_key)

        if self._cloud_mode:
            try:
                self.client = QdrantClient(url=url, api_key=api_key, timeout=30)
                self.client.get_collections()
                self._available = True
                logger.info("qdrant_cloud_connected", url=url)
            except Exception as exc:
                logger.warning(
                    "qdrant_cloud_unavailable",
                    error=str(exc),
                    fallback="in-memory",
                )
                self.client = QdrantClient(":memory:")
                self._cloud_mode = False
                self._available = True
        else:
            self.client = QdrantClient(":memory:")
            self._available = True
            logger.info(
                "qdrant_in_memory",
                note="Set QDRANT_URL + QDRANT_API_KEY to enable Cloud persistence",
            )

    @property
    def available(self) -> bool:
        return self._available

    @property
    def storage_mode(self) -> str:
        return "cloud" if self._cloud_mode else "in-memory"

    def create_collection_if_not_exists(self) -> bool:
        if not self._available:
            return False
        try:
            existing = [c.name for c in self.client.get_collections().collections]
            if self.collection_name in existing:
                logger.info("qdrant_collection_exists", name=self.collection_name)
                return True
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=qdrant_models.VectorParams(
                    size=self.dimension,
                    distance=qdrant_models.Distance.COSINE,
                ),
            )
            logger.info(
                "qdrant_collection_created",
                name=self.collection_name,
                dimension=self.dimension,
                mode=self.storage_mode,
            )
            return True
        except Exception as exc:
            logger.error("qdrant_create_collection_failed", error=str(exc))
            return False

    def upsert_chunk(
        self, chunk_id: str, vector: List[float], metadata: Dict
    ) -> bool:
        if not self._available:
            return False
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=chunk_id, vector=vector, payload=metadata
                    )
                ],
            )
            logger.debug("qdrant_chunk_upserted", chunk_id=chunk_id)
            return True
        except Exception as exc:
            logger.error("qdrant_upsert_failed", chunk_id=chunk_id, error=str(exc))
            return False

    def upsert_chunks_batch(
        self, chunks: List[Tuple[str, List[float], Dict]]
    ) -> int:
        if not self._available or not chunks:
            return 0

        total_upserted = 0
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            points = [
                qdrant_models.PointStruct(id=cid, vector=vec, payload=meta)
                for cid, vec, meta in batch
            ]
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                )
                total_upserted += len(batch)
                logger.debug(
                    "qdrant_batch_upserted",
                    batch_size=len(batch),
                    total_so_far=total_upserted,
                )
            except Exception as exc:
                logger.error("qdrant_batch_upsert_failed", batch_start=i, error=str(exc))

        logger.info(
            "qdrant_upsert_complete",
            total=total_upserted,
            mode=self.storage_mode,
        )
        return total_upserted

    def query(
        self,
        vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        if not self._available:
            return []

        qdrant_filter = None
        if filters:
            conditions = [
                qdrant_models.FieldCondition(
                    key=k, match=qdrant_models.MatchValue(value=v)
                )
                for k, v in filters.items()
            ]
            qdrant_filter = qdrant_models.Filter(must=conditions)

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                query_filter=qdrant_filter,
                limit=top_k,
                with_payload=True,
            )
            return [
                {"id": str(r.id), "score": r.score, "metadata": r.payload}
                for r in results
            ]
        except Exception as exc:
            logger.error("qdrant_query_failed", error=str(exc))
            return []

    def delete_collection(self) -> bool:
        if not self._available:
            return False
        try:
            self.client.delete_collection(self.collection_name)
            logger.info("qdrant_collection_deleted", name=self.collection_name)
            return True
        except Exception as exc:
            logger.error("qdrant_delete_failed", error=str(exc))
            return False

    def get_collection_stats(self) -> Dict:
        if not self._available:
            return {"status": "unavailable"}
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "status": "ok",
                "mode": self.storage_mode,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "dimension": self.dimension,
                "collection": self.collection_name,
            }
        except Exception as exc:
            logger.error("qdrant_stats_failed", error=str(exc))
            return {"status": "error", "error": str(exc)}
