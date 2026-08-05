from typing import List, Dict, Any, Optional
import numpy as np
import logging
import json
from pathlib import Path

from .embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ذخیره‌سازی برداری برای جستجوی معنایی
    """

    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.documents = []
        self.embeddings = []
        self._index_path = Path("data/vector_store.json")

        self._load()

        logger.info(f"✅ Vector Store initialized with {len(self.documents)} documents")

    def add_document(self, document: Dict[str, Any]) -> bool:
        try:
            text = document.get("text") or document.get("content")
            if not text:
                logger.warning("⚠️ Document has no text/content")
                return False

            embedding = self.embedding_service.get_embedding(text)

            if embedding is None:
                return False

            self.documents.append({
                "id": document.get("id", f"doc_{len(self.documents)}"),
                "text": text,
                "metadata": document.get("metadata", {}),
                "created_at": document.get("created_at")
            })

            self.embeddings.append(embedding)

            self._save()

            return True

        except Exception as e:
            logger.error(f"❌ Error adding document to vector store: {e}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        if not self.documents:
            return []

        query_embedding = self.embedding_service.get_embedding(query)

        if query_embedding is None:
            return []

        similarities = []
        query_vec = np.array(query_embedding)

        for i, doc_emb in enumerate(self.embeddings):
            doc_vec = np.array(doc_emb)
            similarity = self._cosine_similarity(query_vec, doc_vec)

            if similarity >= threshold:
                similarities.append({
                    "index": i,
                    "score": similarity,
                    "document": self.documents[i]
                })

        similarities.sort(key=lambda x: x["score"], reverse=True)

        results = []
        for item in similarities[:top_k]:
            result = item["document"].copy()
            result["score"] = item["score"]
            results.append(result)

        return results

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def _save(self):
        try:
            data = {
                "documents": self.documents,
                "embeddings": [emb.tolist() if isinstance(emb, np.ndarray) else emb for emb in self.embeddings]
            }

            self._index_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self._index_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"❌ Error saving vector store: {e}")

    def _load(self):
        try:
            if not self._index_path.exists():
                return

            with open(self._index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.documents = data.get("documents", [])
            self.embeddings = [np.array(emb) for emb in data.get("embeddings", [])]

        except Exception as e:
            logger.error(f"❌ Error loading vector store: {e}")

    def delete_document(self, doc_id: str) -> bool:
        try:
            for i, doc in enumerate(self.documents):
                if doc.get("id") == doc_id:
                    self.documents.pop(i)
                    self.embeddings.pop(i)
                    self._save()
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error deleting document: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_documents": len(self.documents),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0
        }


_vector_store = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
