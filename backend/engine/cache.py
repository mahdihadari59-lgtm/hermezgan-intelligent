#!/usr/bin/env python3  
# -*- coding: utf-8 -*-  
  
"""  
HDP Query Cache  
Thread-safe LRU + TTL Cache  
"""  
  
import time  
import threading  
from collections import OrderedDict  
  
  
class QueryCache:  
    """  
    Thread-safe cache with TTL.  
    """  
  
    def __init__(self, max_size=100, ttl=300):  
        self.max_size = max_size  
        self.ttl = ttl  
  
        self.cache = OrderedDict()  
        self.timestamps = {}  
  
        self.lock = threading.RLock()  
  
        self.hits = 0  
        self.misses = 0  
  
    def _expired(self, key):  
        return (  
            time.time() - self.timestamps.get(key, 0)  
        ) > self.ttl  
  
    def get(self, key):  
        with self.lock:  
  
            if key not in self.cache:  
                self.misses += 1  
                return None  
  
            if self._expired(key):  
                self.cache.pop(key, None)  
                self.timestamps.pop(key, None)  
                self.misses += 1  
                return None  
  
            self.cache.move_to_end(key)  
  
            self.hits += 1  
  
            return self.cache[key]  
  
    def set(self, key, value):  
  
        with self.lock:  
  
            if key in self.cache:  
                self.cache.move_to_end(key)  
  
            self.cache[key] = value  
            self.timestamps[key] = time.time()  
  
            while len(self.cache) > self.max_size:  
                oldest = next(iter(self.cache))  
                self.cache.pop(oldest, None)  
                self.timestamps.pop(oldest, None)  
  
    def invalidate(self, key=None):  
  
        with self.lock:  
  
            if key is None:  
                self.cache.clear()  
                self.timestamps.clear()  
                return  
  
            self.cache.pop(key, None)  
            self.timestamps.pop(key, None)  
  
    def clear(self):  
        self.invalidate()  
  
    def stats(self):  
  
        total = self.hits + self.misses  
  
        hit_rate = (  
            (self.hits / total) * 100  
            if total else 0  
        )  
  
        return {  
            "items": len(self.cache),  
            "hits": self.hits,  
            "misses": self.misses,  
            "hit_rate": round(hit_rate, 2)  
        }  
  
  
if __name__ == "__main__":  
  
    c = QueryCache(max_size=2, ttl=2)  
  
    c.set("a", 100)  
    c.set("b", 200)  
  
    print(c.get("a"))  
  
    c.set("c", 300)  
  
    print(c.get("b"))  
  
    time.sleep(3)  
  
    print(c.get("a"))  
  
    print(c.stats())  
  
