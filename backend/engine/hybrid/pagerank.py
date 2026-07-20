#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/pagerank.py
-------------------------------------------------------
محاسبه امتیاز اهمیت هر نود در گراف دانش با الگوریتم PageRank
(روش کلاسیک Power Iteration)، کاملاً با پایتون خالص — بدون
numpy/scipy/networkx.

کاربرد: نودهایی که یال‌های ورودی زیادی دارند (مثلاً یک بیمارستان
که از چند نود دیگر بهش لینک داده شده) باید در نتایج جستجو
اولویت بالاتری بگیرند؛ این امتیاز به‌عنوان یک سیگنال اضافه به
HybridRanker قابل تزریق است.

نتیجه در همون embedding_storage با model_name="pagerank" (به‌صورت
بردار تک‌عضوی [score]) ذخیره می‌شود تا قابل query شدن سریع باشد.
-------------------------------------------------------
"""

import sqlite3
from typing import Dict, Optional, List

from engine.hybrid.config import HybridConfig
from engine.hybrid.embedding_storage import EmbeddingStorage
from engine.hybrid.constants import EMBEDDING_MODEL_PAGERANK


class PageRankEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        damping: float = 0.85,
        max_iterations: int = 100,
        tolerance: float = 1e-6,
        storage: Optional[EmbeddingStorage] = None,
    ):
        self.db_path = db_path or HybridConfig.DB_PATH
        self.damping = damping
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.storage = storage or EmbeddingStorage(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_graph(self) -> Dict[int, List[int]]:
        """گراف را به‌صورت adjacency list (بدون جهت) بارگذاری می‌کند."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM graph_nodes")
            all_ids = [r["id"] for r in cur.fetchall()]

            adjacency: Dict[int, List[int]] = {node_id: [] for node_id in all_ids}

            cur.execute("SELECT source_id, target_id FROM graph_edges")
            for row in cur.fetchall():
                s, t = row["source_id"], row["target_id"]
                if s in adjacency and t in adjacency:
                    adjacency[s].append(t)
                    adjacency[t].append(s)  # بدون جهت؛ برای گراف جهت‌دار می‌توان حذف کرد

            return adjacency
        finally:
            conn.close()

    def compute(self) -> Dict[int, float]:
        """
        محاسبه PageRank با power iteration استاندارد.
        @returns: {node_id: score} — امتیازها مجموعشون تقریبا ۱ است.
        """
        adjacency = self._load_graph()
        n = len(adjacency)
        if n == 0:
            return {}

        scores: Dict[int, float] = {node_id: 1.0 / n for node_id in adjacency}
        dangling_nodes = [node_id for node_id, neighbors in adjacency.items() if not neighbors]

        for _ in range(self.max_iterations):
            new_scores: Dict[int, float] = {node_id: (1 - self.damping) / n for node_id in adjacency}

            # سهم نودهای dangling (بدون یال خروجی) به‌طور مساوی بین همه پخش می‌شود
            dangling_sum = sum(scores[node_id] for node_id in dangling_nodes)
            if dangling_sum:
                distributed = self.damping * dangling_sum / n
                for node_id in new_scores:
                    new_scores[node_id] += distributed

            for node_id, neighbors in adjacency.items():
                if not neighbors:
                    continue
                share = self.damping * scores[node_id] / len(neighbors)
                for neighbor_id in neighbors:
                    new_scores[neighbor_id] += share

            diff = sum(abs(new_scores[k] - scores[k]) for k in scores)
            scores = new_scores
            if diff < self.tolerance:
                break

        return scores

    def compute_and_store(self) -> Dict[int, float]:
        scores = self.compute()
        vectors = {node_id: [score] for node_id, score in scores.items()}
        self.storage.save_many(vectors, model_name=EMBEDDING_MODEL_PAGERANK)
        return scores

    def get_score(self, node_id: int) -> float:
        vec = self.storage.get(node_id, model_name=EMBEDDING_MODEL_PAGERANK)
        return vec[0] if vec else 0.0

    def top_nodes(self, top_k: int = 10) -> List[Dict]:
        all_vectors = self.storage.get_all(model_name=EMBEDDING_MODEL_PAGERANK)
        ranked = sorted(all_vectors.items(), key=lambda kv: kv[1][0], reverse=True)[:top_k]
        return [{"id": node_id, "score": round(vec[0], 6)} for node_id, vec in ranked]


if __name__ == "__main__":
    import json

    engine = PageRankEngine()
    scores = engine.compute_and_store()
    print(json.dumps({"n_nodes": len(scores), "top": engine.top_nodes(5)}, ensure_ascii=False, indent=2))
