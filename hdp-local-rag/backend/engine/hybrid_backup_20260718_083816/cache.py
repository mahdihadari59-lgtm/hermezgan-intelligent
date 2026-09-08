# -*- coding: utf-8 -*-

"""
engine/hybrid/cache.py
----------------------------------------------------
Hybrid Cache Engine

• Thread Safe
• TTL Cache
• LRU Eviction
• Pure Python
• Termux Compatible
----------------------------------------------------
"""

import time
import threading
from collections import OrderedDict


class HybridCache:

    def __init__(self, max_size=512, ttl=300):
        self.max_size = max_size
        self.ttl = ttl

        self._cache = OrderedDict()
        self._lock = threading.RLock()

        self.hits = 0
        self.misses = 0

    # --------------------------------------------------

    def get(self, key):

        now = time.time()

        with self._lock:

            if key not in self._cache:
                self.misses += 1
                return None

            value, expire = self._cache[key]

            if expire < now:
                del self._cache[key]
                self.misses += 1
                return None

            self._cache.move_to_end(key)

            self.hits += 1

            return value

    # --------------------------------------------------

    def put(self, key, value):

        expire = time.time() + self.ttl

        with self._lock:

            if key in self._cache:
                del self._cache[key]

            self._cache[key] = (value, expire)

            self._cache.move_to_end(key)

            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    # --------------------------------------------------
    # Compatibility Layer
    # --------------------------------------------------

    def set(self, key, value):
        """Backward compatibility"""
        return self.put(key, value)

    def delete(self, key):
        """Backward compatibility"""
        return self.remove(key)

    # --------------------------------------------------

    def remove(self, key):

        with self._lock:

            if key in self._cache:
                del self._cache[key]

    # --------------------------------------------------

    def clear(self):

        with self._lock:
            self._cache.clear()

    # --------------------------------------------------

    def cleanup(self):

        now = time.time()

        with self._lock:

            expired = [
                k
                for k, (_, exp) in self._cache.items()
                if exp < now
            ]

            for k in expired:
                del self._cache[k]

    # --------------------------------------------------

    def stats(self):

        total = self.hits + self.misses

        ratio = 0.0

        if total:
            ratio = self.hits / total

        return {

            "items": len(self._cache),

            "hits": self.hits,

            "misses": self.misses,

            "hit_ratio": round(ratio, 3),

            "ttl": self.ttl,

            "max_size": self.max_size

        }

    # --------------------------------------------------

    def __len__(self):
        return len(self._cache)

    # --------------------------------------------------

    def __contains__(self, key):
        return self.get(key) is not None


# ------------------------------------------------------
# Singleton
# ------------------------------------------------------

default_cache = HybridCache()
