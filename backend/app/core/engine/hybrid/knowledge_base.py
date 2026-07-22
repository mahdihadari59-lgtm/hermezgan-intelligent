from typing import List, Dict, Any, Optional
import logging
import json
from pathlib import Path
from datetime import datetime

from .embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    پایگاه دانش برای ذخیره اطلاعات ساختاریافته
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.documents = []
        self.categories = {}
        self._index_path = Path("data/knowledge_base.json")

        self._load()

        logger.info(f"✅ Knowledge Base initialized with {len(self.documents)} documents")

    def add_document(
        self,
        document: Dict[str, Any],
        category: Optional[str] = None
    ) -> bool:
        try:
            doc_id = document.get("id") or f"doc_{len(self.documents) + 1}"

            doc = {
                "id": doc_id,
                "title": document.get("title", ""),
                "content": document.get("content", ""),
                "metadata": document.get("metadata", {}),
                "category": category or document.get("category", "general"),
                "created_at": document.get("created_at") or datetime.utcnow().isoformat()
            }

            self.documents.append(doc)

            if category:
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(doc_id)

            self._save()

            logger.info(f"📚 Document added to knowledge base: {doc['title']}")
            return True

        except Exception as e:
            logger.error(f"❌ Error adding document to knowledge base: {e}")
            return False

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()

        documents = self.documents
        if category:
            doc_ids = self.categories.get(category, [])
            documents = [doc for doc in documents if doc["id"] in doc_ids]

        for doc in documents:
            score = self._calculate_score(doc, query_lower)

            if score > 0:
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "category": doc["category"],
                    "metadata": doc["metadata"],
                    "score": score,
                    "_source": "knowledge"
                })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def _calculate_score(self, doc: Dict[str, Any], query: str) -> float:
        score = 0

        if query in doc["title"].lower():
            score += 0.4

        content_lower = doc["content"].lower()
        if query in content_lower:
            score += 0.3

        for key, value in doc["metadata"].items():
            if isinstance(value, str) and query in value.lower():
                score += 0.1

        if doc["category"] and query in doc["category"].lower():
            score += 0.2

        return min(score, 1.0)

    def get_document(self, doc_id: str) -> Optional[Dict]:
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None

    def delete_document(self, doc_id: str) -> bool:
        try:
            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]

            for category, doc_ids in self.categories.items():
                if doc_id in doc_ids:
                    self.categories[category] = [d for d in doc_ids if d != doc_id]

            self._save()
            return True

        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            return False

    def get_categories(self) -> List[str]:
        return list(self.categories.keys())

    def get_documents_by_category(self, category: str) -> List[Dict]:
        doc_ids = self.categories.get(category, [])
        return [doc for doc in self.documents if doc["id"] in doc_ids]

    def _save(self):
        try:
            data = {
                "documents": self.documents,
                "categories": self.categories
            }

            self._index_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"❌ Error saving knowledge base: {e}")

    def _load(self):
        try:
            if not self._index_path.exists():
                return

            with open(self._index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.documents = data.get("documents", [])
            self.categories = data.get("categories", {})

        except Exception as e:
            logger.error(f"❌ Error loading knowledge base: {e}")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents),
            "total_categories": len(self.categories),
            "documents_per_category": {
                cat: len(docs) for cat, docs in self.categories.items()
            }
        }


_knowledge_base = None


def get_knowledge_base() -> KnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBase()
    return _knowledge_base
