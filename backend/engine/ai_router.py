"""
engine/__init__.py
------------------------------------
HDP X1 Engine Package
------------------------------------
"""

from engine.hybrid.hybrid_engine import HybridEngine
from engine.graph_search_engine_v2 import GraphSearchEngineV2 as GraphEngine
from engine.fts_engine import FTSEngine
from engine.intent_engine import IntentEngine
from engine.synonym_engine import SynonymEngine
from engine.rerank_engine import ReRankEngine


class AIRouter:
    """
    Main AI Router for HDP X1
    Combines all search engines with hybrid ranking
    """

    def __init__(self, db_path: str):
        """
        Initialize AI Router with all engines
        
        Args:
            db_path: Path to database
        """
        # Initialize all engines
        self.graph = GraphEngine()
        self.fts = FTSEngine(db_path)
        self.intent = IntentEngine(db_path)
        self.synonym = SynonymEngine(db_path)
        self.reranker = ReRankEngine()
        
        # Initialize Hybrid Engine
        self.hybrid = HybridEngine(db_path)

    def ask(self, query: str):
        """
        Process query through all engines with hybrid ranking
        
        Args:
            query: User query string
            
        Returns:
            Reranked results from all engines
        """
        all_results = []

        # 1. Intent Engine
        all_results.extend(
            self.intent.search(query)
        )

        # 2. Synonyms
        synonyms = self.synonym.search(query)
        all_results.extend(synonyms)

        # 3. Hybrid Engine (Graph + FTS + Vector)
        hybrid_results = self.hybrid.search(query)
        if hybrid_results:
            all_results.extend(hybrid_results)

        # 4. Graph Engine
        all_results.extend(
            self.graph.search(query)
        )

        # 5. FTS Engine
        all_results.extend(
            self.fts.search(query)
        )

        # 6. If synonyms found, search with them too
        for syn in synonyms:
            word = syn.get("title", "")
            if word:
                # Graph search with synonym
                all_results.extend(
                    self.graph.search(word)
                )
                # FTS search with synonym
                all_results.extend(
                    self.fts.search(word)
                )

        # Final reranking
        return self.reranker.rerank(query, all_results)

    def close(self):
        """Close all engine connections"""
        self.graph.close()
        self.fts.close()
        if hasattr(self.hybrid, 'close'):
            self.hybrid.close()


# =======================================================
# Convenience Functions
# =======================================================

def create_router(db_path: str) -> AIRouter:
    """Create and initialize AI Router"""
    return AIRouter(db_path)


# =======================================================
# Module Exports
# =======================================================

__all__ = [
    'AIRouter',
    'HybridEngine',
    'GraphEngine',
    'FTSEngine',
    'IntentEngine',
    'SynonymEngine',
    'ReRankEngine',
    'create_router',
]
