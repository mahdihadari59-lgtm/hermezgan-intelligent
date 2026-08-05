import redis
from typing import Optional, Any
import json
import hashlib

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600

    def _get_key(self, prefix: str, *args) -> str:
        key_str = f"{prefix}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        try:
            cached = self.redis_client.get(key)
            return json.loads(cached) if cached else None
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.redis_client.exists(key))
        except Exception:
            return False

    def get_or_set(self, key: str, callback, ttl: Optional[int] = None) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = callback()
        if value is not None:
            self.set(key, value, ttl)
        return value

_cache_manager = None

def get_cache_manager() -> CacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
