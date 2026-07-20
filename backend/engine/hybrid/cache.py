#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/cache.py
-------------------------------------------------------
کش ساده درون‌حافظه‌ای (in-memory) با TTL و محدودیت اندازه
(LRU-like با eviction ساده). برای جلوگیری از اجرای مکرر
جستجوهای سنگین (BM25 + graph expansion) روی query های تکراری.

عمداً بدون هیچ وابستگی خارجی (نه redis، نه functools.lru_cache
چون آن TTL ندارد). مناسب یک پردازش تکی روی Termux؛ برای چند
process هم‌زمان باید به یک کش مشترک (مثل SQLite یا فایل) ارتقا یابد.
-------------------------------------------------------
"""

import time
from collections import OrderedDict
from typing import Any, Optional, Callable

from engine.hybrid.config import HybridConfig


class TTLCache:
    def __init__(self, max_size: Optional[int] = None, ttl_seconds: Optional[int] = None):
        self.max_size = max_size or HybridConfig.CACHE_SIZE
        self.ttl_seconds = ttl_seconds or HybridConfig.CACHE_TTL
        self._store: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _is_expired(self, timestamp: float) -> bool:
        return (time.time() - timestamp) > self.ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            self.misses += 1
            return None
        timestamp, value = self._store[key]
        if self._is_expired(timestamp):
            del self._store[key]
            self.misses += 1
            return None
        # جابه‌جایی به انتهای OrderedDict (اخیراً استفاده‌شده = دوردست‌تر از eviction)
        self._store.move_to_end(key)
        self.hits += 1
        return value

    def set(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (time.time(), value)
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)  # حذف قدیمی‌ترین (LRU eviction)

    def get_or_set(self, key: str, compute_fn: Callable[[], Any]) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = compute_fn()
        self.set(key, value)
        return value

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
        self.hits = 0
        self.misses = 0

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "size": len(self._store),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
        }

    @staticmethod
    def make_key(*parts) -> str:
        """ساخت کلید یکسان از چند بخش (مثلا query + expert + top_k)."""
        return "|".join(str(p) for p in parts)
