#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
engine/hybrid/hybrid_ranker.py
----------------------------------------------------

Hybrid Ranker

ترکیب امتیازهای:

- Exact Match
- FTS
- Graph
- Vector
- Expert

----------------------------------------------------
"""

from typing import Dict, List


class HybridRanker:

    def __init__(
        self,
        exact_weight=0.35,
        fts_weight=0.25,
        graph_weight=0.20,
        vector_weight=0.15,
        expert_weight=0.05
    ):

        self.exact_weight = exact_weight
        self.fts_weight = fts_weight
        self.graph_weight = graph_weight
        self.vector_weight = vector_weight
        self.expert_weight = expert_weight

    # --------------------------------------------------

    def score(
        self,
        exact_score=0.0,
        fts_score=0.0,
        graph_score=0.0,
        vector_score=0.0,
        expert_score=0.0
    ):

        final_score = (

            exact_score * self.exact_weight +

            fts_score * self.fts_weight +

            graph_score * self.graph_weight +

            vector_score * self.vector_weight +

            expert_score * self.expert_weight

        )

        return round(float(final_score), 6)

    # --------------------------------------------------

    def rerank(
        self,
        results: List[Dict]
    ) -> List[Dict]:

        ranked = []

        for item in results:

            final_score = self.score(

                exact_score=item.get(
                    "exact_score",
                    0.0
                ),

                fts_score=item.get(
                    "fts_score",
                    0.0
                ),

                graph_score=item.get(
                    "graph_score",
                    0.0
                ),

                vector_score=item.get(
                    "vector_score",
                    0.0
                ),

                expert_score=item.get(
                    "expert_score",
                    0.0
                )

            )

            item["final_score"] = final_score

            ranked.append(item)

        ranked.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return ranked

    # --------------------------------------------------

    def rank(self, results):
        """
        سازگاری با نسخه‌های قدیمی Engine
        """
        return self.rerank(results)

    # --------------------------------------------------

    def top_k(
        self,
        results: List[Dict],
        k=10
    ):

        return self.rerank(results)[:k]

    # --------------------------------------------------

    def explain(
        self,
        item: Dict
    ):

        return {

            "exact": item.get(
                "exact_score",
                0.0
            ),

            "fts": item.get(
                "fts_score",
                0.0
            ),

            "graph": item.get(
                "graph_score",
                0.0
            ),

            "vector": item.get(
                "vector_score",
                0.0
            ),

            "expert": item.get(
                "expert_score",
                0.0
            ),

            "final": item.get(
                "final_score",
                0.0
            )

        }


hybrid_ranker = HybridRanker()
