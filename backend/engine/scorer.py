#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Score Engine
Score normalization and weighting.
"""

from typing import Dict, List


class ScoreEngine:
    """
    Normalize and weight search scores.
    """

    DEFAULT_WEIGHTS = {
        "graph": 2.5,
        "fts": 2.0,
        "intent": 1.5,
        "synonym": 1.0,
    }

    def __init__(self, weights=None):
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def weight(self, result: Dict) -> Dict:
        source = result.get("source", "").lower()
        weight = self.weights.get(source, 1.0)

        result["raw_score"] = result.get("score", 0.0)
        result["score"] = result["raw_score"] * weight

        return result

    def weight_all(self, results: List[Dict]) -> List[Dict]:
        return [self.weight(r) for r in results]

    def diversity_bonus(self, result: Dict) -> Dict:
        sources = result.get("sources", [])

        if len(sources) > 1:
            bonus = 1 + ((len(sources) - 1) * 0.10)
            result["score"] *= bonus
            result["diversity_bonus"] = round(bonus, 2)
        else:
            result["diversity_bonus"] = 1.0

        return result

    def diversity_all(self, results: List[Dict]) -> List[Dict]:
        return [self.diversity_bonus(r) for r in results]

    def apply(self, results, source):
        """
        سازگاری با Pipeline v3/v4
        """

        if not results:
            return []

        for r in results:
            r["source"] = source

        return self.weight_all(results)

    def summary(self):
        return {
            "weights": self.weights
        }


if __name__ == "__main__":

    engine = ScoreEngine()

    sample = [
        {
            "title": "AI",
            "source": "graph",
            "score": 10
        },
        {
            "title": "Python",
            "source": "fts",
            "score": 8
        }
    ]

    sample = engine.weight_all(sample)

    for item in sample:
        print(item)

    print(engine.summary())
