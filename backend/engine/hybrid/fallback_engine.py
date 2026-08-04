#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/fallback_engine.py
--------------------------------------------------------
Fallback Semantic Engine

زمانی استفاده می‌شود که:
- Vector Search در دسترس نباشد
- امتیاز اعتماد پایین باشد
- خروجی جایگزین برای کاربر لازم باشد

نسخهٔ فعلی بدون وابستگی خارجی پیاده‌سازی شده است.
--------------------------------------------------------
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, Iterable, List, Optional


class FallbackEngine:
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = int(embedding_dim)

    def encode(self, text: Optional[str]) -> List[float]:
        text = (text or "").strip()
        if not text:
            return [0.0] * self.embedding_dim

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector = [(digest[i % len(digest)] / 255.0) for i in range(self.embedding_dim)]

        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def cosine_similarity(self, vec1: Iterable[float], vec2: Iterable[float]) -> float:
        v1 = list(vec1 or [])
        v2 = list(vec2 or [])
        if not v1 or not v2:
            return 0.0

        denom = math.sqrt(sum(x * x for x in v1)) * math.sqrt(sum(x * x for x in v2))
        if denom == 0:
            return 0.0

        return float(sum(a * b for a, b in zip(v1, v2)) / denom)

    def search(self, query: str, nodes: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        query_vec = self.encode(query)
        results: List[Dict[str, Any]] = []

        for node in nodes or []:
            text = f"{node.get('title', '')} {node.get('content', '')}"
            node_vec = self.encode(text)
            score = self.cosine_similarity(query_vec, node_vec)

            results.append(
                {
                    "id": node.get("id"),
                    "score": round(score, 6),
                    "title": node.get("title"),
                    "content": node.get("content"),
                }
            )

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_fallback(
        self,
        query: str,
        expert: Optional[str] = None,
        domain: str = "",
        intent_alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []

        if intent_alternatives:
            for item in intent_alternatives[:5]:
                title = item.get("title") or item.get("name") or item.get("label")
                if title:
                    items.append(
                        {
                            "title": title,
                            "score": round(float(item.get("score", 0.0) or 0.0), 4),
                        }
                    )

        return {
            "query": query,
            "expert": expert,
            "domain": domain,
            "answer": "اطلاعات کافی در پایگاه دانش موجود نیست.",
            "items": items,
            "source": "fallback",
        }


fallback_engine = FallbackEngine()
