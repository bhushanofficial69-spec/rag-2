import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import UnexpectedResponse

from utils.logger import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 100


class VectorDBClient:
    def __init__(self, url: str, api_key: str, collection_name: str, dimension: int = 384):
        self.collection_name = collection_name
        self.dimension = dimension
        self._available = False

        try:
            self.client = QdrantClient(url=url, api_key=api_key, timeout=30)
            self.client.get_collections()
            self._available = True
            logger.info("qdrant_connected", url=url, collection=collection_name)
        except Exception as exc:
            self.client = None
            logger.warning("qdrant_unavailable", error=str(exc))

    @property
    def available(self) -> bool:
        return self._available

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
                        id=chunk_id,
                        vector=vector,
                        payload=metadata,
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
                qdrant_models.PointStruct(
                    id=cid, vector=vec, payload=meta
                )
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
                logger.error(
                    "qdrant_batch_upsert_failed",
                    batch_start=i,
                    error=str(exc),
                )

        logger.info("qdrant_upsert_complete", total=total_upserted)
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
                    key=k,
                    match=qdrant_models.MatchValue(value=v),
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
                {
                    "id": str(r.id),
                    "score": r.score,
                    "metadata": r.payload,
                }
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
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "dimension": self.dimension,
                "collection": self.collection_name,
            }
        except Exception as exc:
            logger.error("qdrant_stats_failed", error=str(exc))
            return {"status": "error", "error": str(exc)}
