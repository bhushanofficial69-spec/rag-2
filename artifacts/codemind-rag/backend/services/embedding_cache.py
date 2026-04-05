from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, List[float]] = {}
        self._max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, text_hash: str) -> Optional[List[float]]:
        if text_hash in self._cache:
            self.hits += 1
            logger.debug("embedding_cache_hit", hash=text_hash[:12])
            return self._cache[text_hash]
        self.misses += 1
        return None

    def set(self, text_hash: str, vector: List[float]) -> None:
        if len(self._cache) >= self._max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[text_hash] = vector
        logger.debug("embedding_cache_set", hash=text_hash[:12])

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 4) if total > 0 else 0.0,
            "size": len(self._cache),
        }

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0
