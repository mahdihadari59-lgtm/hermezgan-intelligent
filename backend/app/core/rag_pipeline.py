import hashlib
from typing import List, Dict, Any, Optional

class RAGPipeline:
    def __init__(self):
        self.initialized = True
        self._knowledge_base = []
        self._embeddings = {}

    @property
    def knowledge_base(self):
        return self._knowledge_base

    def _generate_embedding(self, text: str) -> List[float]:
        hash_bytes = hashlib.md5(text.encode()).digest()
        return [float(b) / 255.0 for b in hash_bytes][:32]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        n1 = sum(a * a for a in vec1) ** 0.5
        n2 = sum(b * b for b in vec2) ** 0.5
        if n1 == 0 or n2 == 0:
            return 0.0
        return dot / (n1 * n2)

    def load_knowledge_base(self, entities: List[Dict[str, Any]]) -> None:
        self._knowledge_base = entities
        for entity in entities:
            text = f"{entity.get('name', '')} {entity.get('description', '')}"
            emb = self._generate_embedding(text)
            self._embeddings[entity.get('entity_id', id(entity))] = emb

    def retrieve(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        if not self._knowledge_base:
            return []
        query_emb = self._generate_embedding(query)
        results = []
        for entity in self._knowledge_base:
            eid = entity.get('entity_id', id(entity))
            if eid in self._embeddings:
                sim = self._cosine_similarity(query_emb, self._embeddings[eid])
                if sim >= threshold:
                    results.append({**entity, "similarity": sim})
        results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        return results[:top_k]

    def generate_context(self, docs: List[Dict[str, Any]]) -> str:
        if not docs:
            return "هیچ اطلاعاتی یافت نشد."
        context = "اطلاعات مرتبط:\n"
        for i, doc in enumerate(docs, 1):
            name = doc.get('name', 'نامشخص')
            desc = doc.get('description', '')
            context += f"{i}. {name}: {desc}\n"
        return context

    def generate_response(self, query: str, context: str, intent: str) -> str:
        if not context or "هیچ اطلاعاتی" in context:
            return "متأسفانه اطلاعاتی برای پاسخ یافت نشد."
        response = f"بر اساس اطلاعات موجود:\n{context}\n"
        if "hospital" in intent:
            response += "نزدیک‌ترین بیمارستان‌ها یافت شد."
        else:
            response += "اطلاعات مورد نظر شما پیدا شد."
        return response

    def process(self, query: str) -> Dict[str, Any]:
        if not query:
            return {
                "query": query,
                "response": "لطفاً یک سوال وارد کنید.",
                "context": "",
                "docs": [],
                "intent": "general",
                "retrieved_documents": []
            }
        docs = self.retrieve(query)
        context = self.generate_context(docs)
        intent = "general"
        if "بیمارستان" in query:
            intent = "hospital"
        elif "رستوران" in query:
            intent = "restaurant"
        response = self.generate_response(query, context, intent)
        return {
            "query": query,
            "response": response,
            "context": context,
            "docs": docs,
            "intent": intent,
            "retrieved_documents": docs
        }


_rag_instance = None

def get_rag_pipeline() -> RAGPipeline:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGPipeline()
    return _rag_instance
