#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Search Pipeline v3.3

Pipeline

Query
 ↓
Intent
 ↓
FTS
 ↓
Graph
 ↓
Hybrid
 ↓
Synonym
 ↓
Merge
 ↓
ReRank
 ↓
Expert   <-- اصلاح شد: قبلاً Search را short-circuit می‌کرد، حالا بعد از
             ReRank اجرا می‌شود و نتایجش merge می‌شود (طبق ممیزی معماری)
 ↓
Answer
"""

import logging

from engine.merger import ResultMerger
from engine.scorer import ScoreEngine
from engine.answer_engine import AnswerEngine

logger = logging.getLogger(__name__)


class SearchPipeline:

    def __init__(
            self,
            engine
    ):

        self.engine = engine

        self.merger = ResultMerger()

        self.scorer = ScoreEngine()

        self.answer = AnswerEngine()

    def run(
            self,
            query,
            context=None
    ):

        context = context or {}

        logger.info(
            f"Pipeline started: {query}"
        )

        # -----------------------------
        # Intent
        # -----------------------------

        intent_results = (
            self.engine.intent.search(
                query
            )
        )

        # -----------------------------
        # FTS
        # -----------------------------

        try:

            fts_results = (
                self.engine.fts.search(
                    query
                )
            )

            fts_results = self.scorer.apply(
                fts_results,
                "fts"
            )

        except Exception as e:

            logger.exception(e)

            fts_results = []

        # -----------------------------
        # Graph
        # -----------------------------

        try:

            graph_results = (
                self.engine.graph.search(
                    query,
                    context
                )
            )

            graph_results = self.scorer.apply(
                graph_results,
                "graph"
            )

        except Exception as e:

            logger.exception(e)

            graph_results = []

        # -----------------------------
        # Hybrid (اصلاح‌شده)
        # -----------------------------

        try:

            hybrid_response = self.engine.hybrid.search(query)

            hybrid_results = self.scorer.apply(
                hybrid_response.get("results", []),
                "hybrid"
            )

        except Exception as e:

            logger.exception(e)

            hybrid_results = []

        # -----------------------------
        # Synonym
        # -----------------------------

        try:

            synonym_results = (
                self.engine.synonym.search(
                    query
                )
            )

            synonym_results = self.scorer.apply(
                synonym_results,
                "synonym"
            )

        except Exception as e:

            logger.exception(e)

            synonym_results = []

        # -----------------------------
        # Intent Weight
        # -----------------------------
        # توجه: dispatcher.dispatch() پایین‌تر روی intent_results خام
        # (قبل از این خط) کار می‌کند نه این‌جا - چون apply() این لیست را
        # درجا (in-place) تغییر می‌دهد. فقط "score" عوض می‌شود، نه
        # "title"، پس ترتیب برای dispatch مشکلی ایجاد نمی‌کند.

        intent_results_weighted = self.scorer.apply(
            intent_results,
            "intent"
        )

        # -----------------------------
        # Merge
        # -----------------------------

        results = self.merger.merge(

            graph_results,

            hybrid_results,

            fts_results,

            synonym_results,

            intent_results_weighted

        )

        # -----------------------------
        # ReRank
        # -----------------------------

        results = self.engine.reranker.rerank(

            query,

            results

        )

        logger.info(
            f"Pipeline finished ({len(results)} generic results)"
        )

        # -----------------------------
        # Expert (اصلاح‌شده: بعد از ReRank، نه جای Search)
        # -----------------------------
        # قبلاً: اگر expert پیدا می‌شد، کل FTS/Graph/Hybrid/Synonym حذف
        # می‌شد. حالا: expert نتایج اضافه/تخصصی می‌دهد که به نتایج عمومی
        # merge می‌شود - بدون rerank دوباره (تا بونوس دوبار اعمال نشود).

        expert = self.engine.dispatcher.dispatch(intent_results)

        if expert:

            try:

                expert_results = expert.search(
                    query,
                    intent_results
                )

                expert_results = self.scorer.apply(
                    expert_results,
                    expert.name
                )

            except Exception as e:

                logger.exception(e)

                expert_results = []

            if expert_results:

                results = self.merger.merge(
                    expert_results,
                    results
                )

                logger.info(
                    f"Expert '{expert.name}' merged "
                    f"({len(expert_results)} results)."
                )

        # -----------------------------
        # Answer
        # -----------------------------

        return self.answer.build(query, results)


if __name__ == "__main__":

    print("HDP Search Pipeline v3.3")
    print("Ready")
