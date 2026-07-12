import redis
import json
from typing import Optional, Any
from app.config import settings

class CacheManager:
    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        data = self.client.get(key)
        if data:
            try:
                return json.loads(data)
            except:
                return data
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.setex(key, ttl, value)
    
    def delete(self, key: str) -> int:
        return self.client.delete(key)
    
    def clear_pattern(self, pattern: str) -> int:
        count = 0
        for key in self.client.scan_iter(match=pattern):
            count += self.client.delete(key)
        return count

cache = CacheManager()
