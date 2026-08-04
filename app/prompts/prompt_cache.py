import time
from typing import Any, Dict, Optional, Tuple
from app.config.settings import settings
from app.utils.logger import logger

class PromptCache:
    """
    In-Memory Prompt Cache for storing loaded prompt templates and rendered static prompt sections.
    Supports TTL expiration, LRU capacity eviction, and hit/miss observability statistics.
    """

    def __init__(self, default_ttl: Optional[int] = None, max_size: Optional[int] = None):
        self.default_ttl = default_ttl if default_ttl is not None else settings.prompt.prompt_cache_ttl
        self.max_size = max_size if max_size is not None else settings.prompt.prompt_cache_max_size
        # Cache entries stored as: key -> (value, expire_at, last_accessed_timestamp)
        self._cache: Dict[str, Tuple[Any, float, float]] = {}
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if present and not expired."""
        if not settings.features.enable_prompt_caching:
            return None

        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        value, expire_at, _ = entry
        now = time.time()

        if now > expire_at:
            # Expired
            del self._cache[key]
            self._misses += 1
            logger.info(f"PromptCache entry expired for key '{key}'", component="PromptCache")
            return None

        # Update last accessed time for LRU tracking
        self._cache[key] = (value, expire_at, now)
        self._hits += 1
        logger.info(f"PromptCache hit for key '{key}'", component="PromptCache")
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stores item in cache with TTL and enforces max_size LRU eviction."""
        if not settings.features.enable_prompt_caching:
            return

        now = time.time()
        effective_ttl = ttl if ttl is not None else self.default_ttl
        expire_at = now + effective_ttl

        # Enforce max size eviction if adding new entry exceeds capacity
        if key not in self._cache and len(self._cache) >= self.max_size:
            self._evict_lru()

        self._cache[key] = (value, expire_at, now)
        logger.info(f"PromptCache stored key '{key}' (TTL={effective_ttl}s)", component="PromptCache")

    def _evict_lru(self) -> None:
        """Evicts the least recently used entry from cache."""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k][2])
        del self._cache[lru_key]
        self._evictions += 1
        logger.info(f"PromptCache evicted LRU entry key '{lru_key}'", component="PromptCache")

    def clear(self) -> None:
        """Clears all cached entries and resets statistics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        logger.info("PromptCache cleared", component="PromptCache")

    @property
    def stats(self) -> Dict[str, Any]:
        """Returns runtime cache statistics."""
        total = self._hits + self._misses
        hit_rate = round(self._hits / total * 100, 2) if total > 0 else 0.0
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_pct": hit_rate,
            "evictions": self._evictions
        }

# Global singleton prompt cache instance
prompt_cache = PromptCache()
