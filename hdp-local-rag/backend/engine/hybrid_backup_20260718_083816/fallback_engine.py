#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
engine/hybrid/fallback_engine.py
--------------------------------------------------------
Fallback Semantic Engine

استفاده زمانی که:

- GAT وجود ندارد
- Embedding ساخته نشده
- Vector Search غیرفعال است

کاملاً بدون وابستگی
Termux Friendly
--------------------------------------------------------
"""

import hashlib
import math
import numpy as np


class FallbackEngine:

    def __init__(self, embedding_dim=128):
        self.embedding_dim = embedding_dim

    # --------------------------------------------------

    def encode(self, text):

        text = (text or "").strip()

        if not text:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        h = hashlib.sha256(text.encode("utf-8")).digest()

        vector = np.zeros(self.embedding_dim, dtype=np.float32)

        for i in range(self.embedding_dim):

            b = h[i % len(h)]

            vector[i] = (b / 255.0)

        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        return vector.astype(np.float32)

    # --------------------------------------------------

    def cosine_similarity(self, vec1, vec2):

        if vec1 is None or vec2 is None:
            return 0.0

        denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)

        if denom == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / denom)

    # --------------------------------------------------

    def search(self, query, nodes, top_k=10):
        """
        nodes =

        [
            {
                "id":1,
                "title":"...",
                "content":"..."
            }
        ]
        """

        query_vec = self.encode(query)

        results = []

        for node in nodes:

            text = f"{node.get('title','')} {node.get('content','')}"

            node_vec = self.encode(text)

            score = self.cosine_similarity(
                query_vec,
                node_vec
            )

            results.append({

                "id": node.get("id"),

                "score": round(score, 6),

                "title": node.get("title"),

                "content": node.get("content")

            })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]


# --------------------------------------------------------

fallback_engine = FallbackEngine()
