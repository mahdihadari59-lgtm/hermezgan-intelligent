from typing import List, Dict, Any, Optional, Tuple
import logging
import json
from datetime import datetime

from .vector_store import VectorStore, get_vector_store
from .graph_store import GraphStore, get_graph_store
from .knowledge_base import KnowledgeBase, get_knowledge_base
from .embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


class HybridEngine:
    """
    موتور هیبرید - ترکیبی از Vector Search + Graph Search + Knowledge Base
    برای جستجوی هوشمند و تولید پاسخ
    """

    def __init__(self):
        self.vector_store = get_vector_store()
        self.graph_store = get_graph_store()
        self.knowledge_base = get_knowledge_base()
        self.embedding_service = get_embedding_service()

        logger.info("✅ Hybrid Engine initialized")

    def search(
        self,
        query: str,
        top_k: int = 10,
        use_vector: bool = True,
        use_graph: bool = True,
        use_knowledge: bool = True,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        جستجوی ترکیبی در تمام منابع

        Args:
            query: عبارت جستجو
            top_k: تعداد نتایج
            use_vector: استفاده از Vector Search
            use_graph: استفاده از Graph Search
            use_knowledge: استفاده از Knowledge Base
            filters: فیلترهای اضافی

        Returns:
            List[Dict]: نتایج جستجو با امتیاز
        """
        results = []

        if use_vector:
            vector_results = self.vector_store.search(query, top_k=top_k)
            for r in vector_results:
                r["_source"] = "vector"
                results.append(r)

        if use_graph:
            graph_results = self.graph_store.search(query, limit=top_k)
            for r in graph_results:
                r["_source"] = "graph"
                results.append(r)

        if use_knowledge:
            kb_results = self.knowledge_base.search(query, limit=top_k)
            for r in kb_results:
                r["_source"] = "knowledge"
                results.append(r)

        merged = self._merge_and_rerank(results, query)

        if filters:
            merged = self._apply_filters(merged, filters)

        return merged[:top_k]

    def _merge_and_rerank(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        grouped = {}
        for item in results:
            item_id = item.get("id") or item.get("_id")
            if not item_id:
                continue

            if item_id not in grouped:
                grouped[item_id] = {
                    "id": item_id,
                    "scores": [],
                    "sources": [],
                    "data": item
                }

            grouped[item_id]["scores"].append(item.get("score", 0.5))
            grouped[item_id]["sources"].append(item.get("_source", "unknown"))

        final_results = []
        for item_id, group in grouped.items():
            avg_score = sum(group["scores"]) / len(group["scores"])

            source_boost = 0
            if "vector" in group["sources"]:
                source_boost += 0.1
            if "knowledge" in group["sources"]:
                source_boost += 0.15
            if "graph" in group["sources"]:
                source_boost += 0.05

            final_score = min(avg_score + source_boost, 1.0)

            group["data"]["_score"] = final_score
            group["data"]["_sources"] = list(set(group["sources"]))
            group["data"]["_source_count"] = len(set(group["sources"]))

            final_results.append(group["data"])

        return sorted(final_results, key=lambda x: x.get("_score", 0), reverse=True)

    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        filtered = []

        for item in results:
            match = True
            for key, value in filters.items():
                if key not in item:
                    match = False
                    break

                if isinstance(value, list):
                    if item[key] not in value:
                        match = False
                        break
                elif item[key] != value:
                    match = False
                    break

            if match:
                filtered.append(item)

        return filtered

    def answer(
        self,
        query: str,
        context: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        search_results = self.search(query, top_k=5)

        if not search_results:
            return {
                "answer": "متأسفانه اطلاعاتی برای پاسخ به سوال شما پیدا نشد.",
                "sources": [],
                "confidence": 0.0
            }

        best_result = search_results[0]
        answer = best_result.get("text") or best_result.get("content") or best_result.get("answer")

        if not answer:
            answer = f"اطلاعات مرتبط با '{query}' یافت شد."

        sources = []
        for r in search_results[:3]:
            source = {
                "title": r.get("title") or r.get("name") or "منبع",
                "type": r.get("_source", "unknown"),
                "score": r.get("_score", 0.5)
            }
            sources.append(source)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": best_result.get("_score", 0.5),
            "context": context
        }

    def add_document(
        self,
        document: Dict[str, Any],
        doc_type: str = "knowledge"
    ) -> bool:
        try:
            if doc_type == "vector":
                return self.vector_store.add_document(document)
            elif doc_type == "graph":
                return self.graph_store.add_node(document)
            elif doc_type == "knowledge":
                return self.knowledge_base.add_document(document)
            else:
                self.vector_store.add_document(document)
                self.graph_store.add_node(document)
                self.knowledge_base.add_document(document)
                return True

        except Exception as e:
            logger.error(f"❌ Error adding document: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        return {
            "vector_store": self.vector_store.get_stats(),
            "graph_store": self.graph_store.get_stats(),
            "knowledge_base": self.knowledge_base.get_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }


_hybrid_engine = None


def get_hybrid_engine() -> HybridEngine:
    global _hybrid_engine
    if _hybrid_engine is None:
        _hybrid_engine = HybridEngine()
    return _hybrid_engine
