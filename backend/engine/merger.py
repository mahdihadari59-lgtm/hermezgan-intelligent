#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Result Merger
Merge + Deduplicate Search Results
"""

from copy import deepcopy


class ResultMerger:

    def __init__(self):
        self.primary_key = "doc_id"

    def merge(self, *result_lists):
        """
        Merge multiple engine results.

        Usage:
            merge(list1,list2,list3)
        """

        merged = {}

        for results in result_lists:

            if not results:
                continue

            for item in results:

                key = (
                    item.get("doc_id")
                    or item.get("id")
                    or item.get("title")
                )

                if key not in merged:

                    obj = deepcopy(item)

                    obj["sources"] = [
                        item.get("source", "unknown")
                    ]

                    obj["scores"] = {
                        item.get("source", "unknown"):
                        item.get("score", 0)
                    }

                    merged[key] = obj

                    continue

                current = merged[key]

                src = item.get("source", "unknown")

                if src not in current["sources"]:
                    current["sources"].append(src)

                current["scores"][src] = item.get(
                    "score",
                    0
                )

                if item.get("score", 0) > current.get("score", 0):

                    current["score"] = item["score"]

                    for field in (
                        "title",
                        "content",
                        "metadata"
                    ):

                        if item.get(field):
                            current[field] = item[field]

        return list(merged.values())

    def diversity_boost(
        self,
        results,
        boost=0.10
    ):
        """
        Boost results found by multiple engines.
        """

        for r in results:

            count = len(
                r.get("sources", [])
            )

            if count > 1:

                r["score"] *= (
                    1 +
                    (count - 1) * boost
                )

                r["diverse_sources"] = True

            else:

                r["diverse_sources"] = False

        return results


if __name__ == "__main__":

    graph = [
        {
            "doc_id": 1,
            "title": "AI",
            "score": 15,
            "source": "graph"
        }
    ]

    fts = [
        {
            "doc_id": 1,
            "title": "AI",
            "score": 10,
            "source": "fts"
        },
        {
            "doc_id": 2,
            "title": "Python",
            "score": 8,
            "source": "fts"
        }
    ]

    merger = ResultMerger()

    merged = merger.merge(
        graph,
        fts
    )

    merged = merger.diversity_boost(
        merged
    )

    for r in merged:
        print(r)

