import redis
import json
from typing import Optional, Any, Dict, List
from datetime import timedelta
import pickle
import logging
from contextlib import contextmanager

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisEngine:
    """
    موتور Redis با قابلیت‌های پیشرفته
    مدیریت اتصال، کش، Pub/Sub، Rate Limiting
    """

    _instance = None
    _client = None
    _pubsub = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """مقداردهی اولیه Redis"""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_URL.split('://')[-1].split(':')[0] if '://' in settings.REDIS_URL else 'localhost',
                port=int(settings.REDIS_URL.split(':')[-1]) if ':' in settings.REDIS_URL else 6379,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )

            # تست اتصال
            self._client.ping()
            logger.info("✅ Redis Engine initialized successfully")

        except Exception as e:
            logger.warning(f"⚠️ Redis initialization failed: {e}")
            self._client = None

    @property
    def client(self):
        return self._client

    @property
    def is_connected(self) -> bool:
        """بررسی اتصال Redis"""
        if not self._client:
            return False
        try:
            self._client.ping()
            return True
        except Exception:
            return False

    # ============================================================
    # Cache Operations
    # ============================================================

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        if not self.is_connected:
            return False

        try:
            if serialize:
                value = json.dumps(value, ensure_ascii=False)

            if ttl:
                return self._client.setex(key, ttl, value)
            return self._client.set(key, value)

        except Exception as e:
            logger.error(f"❌ Redis set error: {e}")
            return False

    def get(self, key: str, deserialize: bool = True) -> Optional[Any]:
        if not self.is_connected:
            return None

        try:
            value = self._client.get(key)
            if value is None:
                return None

            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value

        except Exception as e:
            logger.error(f"❌ Redis get error: {e}")
            return None

    def delete(self, *keys: str) -> int:
        if not self.is_connected:
            return 0

        try:
            return self._client.delete(*keys)
        except Exception as e:
            logger.error(f"❌ Redis delete error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        if not self.is_connected:
            return False

        try:
            return self._client.exists(key) > 0
        except Exception as e:
            logger.error(f"❌ Redis exists error: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        if not self.is_connected:
            return False

        try:
            return self._client.expire(key, ttl)
        except Exception as e:
            logger.error(f"❌ Redis expire error: {e}")
            return False

    def ttl(self, key: str) -> int:
        if not self.is_connected:
            return -2

        try:
            return self._client.ttl(key)
        except Exception as e:
            logger.error(f"❌ Redis ttl error: {e}")
            return -2

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        if not self.is_connected:
            return None

        try:
            return self._client.incrby(key, amount)
        except Exception as e:
            logger.error(f"❌ Redis increment error: {e}")
            return None

    def get_or_set(self, key: str, func, ttl: Optional[int] = None) -> Optional[Any]:
        value = self.get(key)
        if value is not None:
            return value

        value = func()
        if value is not None:
            self.set(key, value, ttl)

        return value

    # ============================================================
    # Hash Operations
    # ============================================================

    def hset(self, key: str, field: str, value: Any) -> bool:
        if not self.is_connected:
            return False

        try:
            return self._client.hset(key, field, json.dumps(value, ensure_ascii=False)) > 0
        except Exception as e:
            logger.error(f"❌ Redis hset error: {e}")
            return False

    def hget(self, key: str, field: str) -> Optional[Any]:
        if not self.is_connected:
            return None

        try:
            value = self._client.hget(key, field)
            if value:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return None
        except Exception as e:
            logger.error(f"❌ Redis hget error: {e}")
            return None

    def hgetall(self, key: str) -> Dict:
        if not self.is_connected:
            return {}

        try:
            data = self._client.hgetall(key)
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            logger.error(f"❌ Redis hgetall error: {e}")
            return {}

    def hdel(self, key: str, *fields: str) -> int:
        if not self.is_connected:
            return 0

        try:
            return self._client.hdel(key, *fields)
        except Exception as e:
            logger.error(f"❌ Redis hdel error: {e}")
            return 0

    # ============================================================
    # List Operations
    # ============================================================

    def lpush(self, key: str, *values: Any) -> Optional[int]:
        if not self.is_connected:
            return None

        try:
            serialized = [json.dumps(v, ensure_ascii=False) for v in values]
            return self._client.lpush(key, *serialized)
        except Exception as e:
            logger.error(f"❌ Redis lpush error: {e}")
            return None

    def rpush(self, key: str, *values: Any) -> Optional[int]:
        if not self.is_connected:
            return None

        try:
            serialized = [json.dumps(v, ensure_ascii=False) for v in values]
            return self._client.rpush(key, *serialized)
        except Exception as e:
            logger.error(f"❌ Redis rpush error: {e}")
            return None

    def lpop(self, key: str, deserialize: bool = True) -> Optional[Any]:
        if not self.is_connected:
            return None

        try:
            value = self._client.lpop(key)
            if value and deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
        except Exception as e:
            logger.error(f"❌ Redis lpop error: {e}")
            return None

    def rpop(self, key: str, deserialize: bool = True) -> Optional[Any]:
        if not self.is_connected:
            return None

        try:
            value = self._client.rpop(key)
            if value and deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
        except Exception as e:
            logger.error(f"❌ Redis rpop error: {e}")
            return None

    def lrange(self, key: str, start: int, end: int, deserialize: bool = True) -> List:
        if not self.is_connected:
            return []

        try:
            values = self._client.lrange(key, start, end)
            if deserialize:
                result = []
                for v in values:
                    try:
                        result.append(json.loads(v))
                    except (json.JSONDecodeError, TypeError):
                        result.append(v)
                return result
            return values
        except Exception as e:
            logger.error(f"❌ Redis lrange error: {e}")
            return []

    # ============================================================
    # Set Operations
    # ============================================================

    def sadd(self, key: str, *values: Any) -> Optional[int]:
        if not self.is_connected:
            return None

        try:
            serialized = [json.dumps(v, ensure_ascii=False) for v in values]
            return self._client.sadd(key, *serialized)
        except Exception as e:
            logger.error(f"❌ Redis sadd error: {e}")
            return None

    def smembers(self, key: str, deserialize: bool = True) -> List:
        if not self.is_connected:
            return []

        try:
            values = self._client.smembers(key)
            if deserialize:
                result = []
                for v in values:
                    try:
                        result.append(json.loads(v))
                    except (json.JSONDecodeError, TypeError):
                        result.append(v)
                return result
            return list(values)
        except Exception as e:
            logger.error(f"❌ Redis smembers error: {e}")
            return []

    def sismember(self, key: str, value: Any) -> bool:
        if not self.is_connected:
            return False

        try:
            serialized = json.dumps(value, ensure_ascii=False)
            return self._client.sismember(key, serialized)
        except Exception as e:
            logger.error(f"❌ Redis sismember error: {e}")
            return False

    # ============================================================
    # Pub/Sub Operations
    # ============================================================

    def publish(self, channel: str, message: Any) -> int:
        if not self.is_connected:
            return 0

        try:
            if not isinstance(message, str):
                message = json.dumps(message, ensure_ascii=False)
            return self._client.publish(channel, message)
        except Exception as e:
            logger.error(f"❌ Redis publish error: {e}")
            return 0

    def subscribe(self, *channels: str):
        if not self.is_connected:
            return None

        try:
            self._pubsub = self._client.pubsub()
            self._pubsub.subscribe(*channels)
            return self._pubsub
        except Exception as e:
            logger.error(f"❌ Redis subscribe error: {e}")
            return None

    def get_message(self, timeout: float = 0.1) -> Optional[Dict]:
        if not self.is_connected or not self._pubsub:
            return None

        try:
            message = self._pubsub.get_message(timeout=timeout)
            if message and message.get('data'):
                try:
                    message['data'] = json.loads(message['data'])
                except (json.JSONDecodeError, TypeError):
                    pass
            return message
        except Exception as e:
            logger.error(f"❌ Redis get_message error: {e}")
            return None

    # ============================================================
    # Utility Operations
    # ============================================================

    def keys(self, pattern: str = "*") -> List[str]:
        if not self.is_connected:
            return []

        try:
            return self._client.keys(pattern)
        except Exception as e:
            logger.error(f"❌ Redis keys error: {e}")
            return []

    def clear_pattern(self, pattern: str) -> int:
        if not self.is_connected:
            return 0

        try:
            keys = self.keys(pattern)
            if keys:
                return self.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"❌ Redis clear_pattern error: {e}")
            return 0

    def flush(self) -> bool:
        if not self.is_connected:
            return False

        try:
            self._client.flushdb()
            logger.warning("⚠️ Redis database flushed")
            return True
        except Exception as e:
            logger.error(f"❌ Redis flush error: {e}")
            return False

    def info(self) -> Dict:
        if not self.is_connected:
            return {}

        try:
            return self._client.info()
        except Exception as e:
            logger.error(f"❌ Redis info error: {e}")
            return {}


# ============================================================
# Convenience Functions
# ============================================================

_cache_engine = None


def get_redis_engine() -> RedisEngine:
    """دریافت نمونه Redis Engine"""
    global _cache_engine
    if _cache_engine is None:
        _cache_engine = RedisEngine()
    return _cache_engine


def get_redis() -> Optional[redis.Redis]:
    """دریافت کلاینت Redis"""
    engine = get_redis_engine()
    return engine.client


def get_cache() -> RedisEngine:
    """دریافت موتور کش"""
    return get_redis_engine()
