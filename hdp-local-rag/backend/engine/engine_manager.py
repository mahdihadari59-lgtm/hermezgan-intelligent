#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Engine Manager

Loads and manages all search engines.

Responsibilities:
- Initialize engines
- Health check
- Execute individual engines
- Close resources
"""

import logging

from engine.hybrid.hybrid_engine import HybridEngine
from engine.rerank_engine import ReRankEngine
from engine.expert_dispatcher import ExpertDispatcher
from engine.config import DATABASE_PATH
from engine.intent_engine import IntentEngine
from engine.synonym_engine import SynonymEngine
from engine.graph_search_engine_v2 import GraphSearchEngineV2 as GraphEngine
from engine.fts_engine import FTSEngine

logger = logging.getLogger(__name__)


class EngineManager:

    def __init__(self, db_path):

        self.db_path = db_path

        self.intent = IntentEngine(db_path)
        self.synonym = SynonymEngine(db_path)
        self.hybrid = HybridEngine(self.db_path)
        self.graph = GraphEngine()
        self.fts = FTSEngine(db_path)
        self.reranker = ReRankEngine()
        self.dispatcher = ExpertDispatcher(self)

        logger.info("EngineManager initialized")

    def run_intent(self, query):

        return self.intent.search(query)

    def run_fts(self, query):

        return self.fts.search(query)

    def run_graph(self, query, context=None):

        context = context or {}

        try:
            return self.graph.search(query, context)
        except TypeError:
            return self.graph.search(query)

    def run_synonym(self, query):

        return self.synonym.search(query)

    def run_hybrid(self, query):
        """Run hybrid search (Graph + FTS + Vector)"""
        return self.hybrid.search(query)

    def health(self):

        return {
            "intent": self.intent is not None,
            "fts": self.fts is not None,
            "graph": self.graph is not None,
            "synonym": self.synonym is not None,
            "hybrid": self.hybrid is not None,
            "dispatcher": self.dispatcher is not None,
            "reranker": self.reranker is not None
        }

    def close(self):

        for engine in (
            self.intent,
            self.synonym,
            self.hybrid,
            self.graph,
            self.fts
        ):

            if hasattr(engine, "close"):

                try:
                    engine.close()
                except Exception as e:
                    logger.warning(e)

        if hasattr(self.reranker, "close"):
            self.reranker.close()

        if hasattr(self.dispatcher, "close"):
            self.dispatcher.close()


if __name__ == "__main__":
    m = EngineManager(str(DATABASE_PATH))
    print(m.health())
    m.close()
