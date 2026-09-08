#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/hybrid_ranker.py
-------------------------------------------------------
لایه ترکیب امتیاز چند منبع (کلیدواژه، گراف، برداری، و در
آینده مدل‌های دیگر) به یک لیست نتیجه نهایی مرتب‌شده.

دو روش ترکیب پشتیبانی می‌شود:
    1) Weighted Sum — ترکیب وزن‌دار امتیازهای نرمال‌شده هر منبع
       (مناسب وقتی می‌خواهیم اهمیت نسبی هر منبع را دقیق کنترل کنیم)
    2) Reciprocal Rank Fusion (RRF) — ترکیب بر اساس rank هر منبع
       (مناسب وقتی مقیاس امتیازهای منابع قابل‌مقایسه نیست)

این فایل منطق ترکیبی را که قبلاً داخل hybrid_engine.py هارد-کد
شده بود، به یک کامپوننت مستقل و قابل‌تست تبدیل می‌کند.
-------------------------------------------------------
"""

from typing import Dict, List, Any, Optional


class HybridRanker:
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        rrf_k: int = 60,
    ):
        """
        @param weights: وزن هر منبع در حالت weighted sum.
               مثال: {"keyword": 0.6, "graph": 0.25, "vector": 0.15}
        """
        self.weights = weights or {"keyword": 0.6, "graph": 0.25, "vector": 0.15}
        self.rrf_k = rrf_k

    # -----------------------------------------------------
    # حالت ۱: Weighted Sum
    # -----------------------------------------------------
    def combine_weighted(
        self, sources: Dict[str, Dict[int, float]]
    ) -> Dict[int, Dict[str, Any]]:
        """
        @param sources: دیکشنری {source_name: {node_id: score}}
               مثال: {"keyword": {1: 0.9, 2: 0.3}, "graph": {2: 0.5}}
        @returns: {node_id: {"final": float, "breakdown": {...}}}
        """
        combined: Dict[int, Dict[str, Any]] = {}

        for source_name, node_scores in sources.items():
            weight = self.weights.get(source_name, 0.0)
            for node_id, score in node_scores.items():
                if node_id not in combined:
                    combined[node_id] = {"final": 0.0, "breakdown": {}}
                combined[node_id]["breakdown"][source_name] = score
                combined[node_id]["final"] += score * weight

        # اطمینان از این‌که همه منابع در breakdown حاضرند (حتی با ۰)
        for node_id, data in combined.items():
            for source_name in sources:
                data["breakdown"].setdefault(source_name, 0.0)

        return combined

    # -----------------------------------------------------
    # حالت ۲: Reciprocal Rank Fusion
    # -----------------------------------------------------
    def combine_rrf(self, ranked_lists: Dict[str, List[int]]) -> Dict[int, float]:
        """
        @param ranked_lists: {source_name: [node_id به ترتیب rank]}
        @returns: {node_id: fused_score}
        """
        fused: Dict[int, float] = {}
        for source_name, ranked_ids in ranked_lists.items():
            for rank, node_id in enumerate(ranked_ids, start=1):
                fused[node_id] = fused.get(node_id, 0.0) + 1.0 / (self.rrf_k + rank)
        return fused

    # -----------------------------------------------------
    # ابزار کمکی: تبدیل dict امتیاز به لیست رتبه‌بندی‌شده id
    # -----------------------------------------------------
    @staticmethod
    def scores_to_ranked_ids(scores: Dict[int, float]) -> List[int]:
        return [node_id for node_id, _ in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)]

    def rank(
        self,
        sources: Dict[str, Dict[int, float]],
        method: str = "weighted",
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        نقطه ورود اصلی: امتیازهای خام هر منبع را می‌گیرد و لیست
        نهایی رتبه‌بندی‌شده (فقط id و امتیاز) برمی‌گرداند.
        """
        if method == "rrf":
            ranked_lists = {name: self.scores_to_ranked_ids(scores) for name, scores in sources.items()}
            fused = self.combine_rrf(ranked_lists)
            ordered = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
            return [{"id": node_id, "score": round(score, 4)} for node_id, score in ordered]

        combined = self.combine_weighted(sources)
        ordered = sorted(combined.items(), key=lambda kv: kv[1]["final"], reverse=True)[:top_k]
        return [
            {"id": node_id, "score": round(data["final"], 4), "breakdown": {k: round(v, 4) for k, v in data["breakdown"].items()}}
            for node_id, data in ordered
        ]
