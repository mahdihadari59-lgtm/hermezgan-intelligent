import hashlib
from typing import Any, Optional, Callable
import logging

from app.core.engine.redis_engine import get_cache

logger = logging.getLogger(__name__)


class DataCache:
    """
    کلاس کش داده‌ها با Redis
    """

    def __init__(self):
        self.cache = get_cache()
        self.default_ttl = 3600
        self.prefix = "data_cache"

    def get_key(self, key: str) -> str:
        cache_key = f"{self.prefix}:{key}"
        if len(cache_key) > 100:
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        return cache_key

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        cache_key = self.get_key(key)
        ttl = ttl or self.default_ttl
        return self.cache.set(cache_key, value, ttl)

    def get(self, key: str) -> Optional[Any]:
        cache_key = self.get_key(key)
        return self.cache.get(cache_key)

    def delete(self, key: str) -> bool:
        cache_key = self.get_key(key)
        return self.cache.delete(cache_key) > 0

    def clear_pattern(self, pattern: str) -> int:
        cache_key = self.get_key(pattern)
        return self.cache.clear_pattern(cache_key)

    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        data = func()
        if data is not None:
            self.set(key, data, ttl)
        return data

    def invalidate(self, key: str):
        self.delete(key)

    def invalidate_pattern(self, pattern: str):
        self.clear_pattern(pattern)


_data_cache = None


def get_data_cache() -> DataCache:
    global _data_cache
    if _data_cache is None:
        _data_cache = DataCache()
    return _data_cache
