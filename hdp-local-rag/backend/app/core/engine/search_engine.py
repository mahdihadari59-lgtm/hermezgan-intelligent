import re
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class SearchEngine:
    """
    موتور جستجوی داخلی
    جستجوی متنی با قابلیت فازی و Weighted Scoring
    """

    def __init__(self):
        self._index = {}
        self._documents = {}

    def index_document(self, doc_id: str, content: Dict[str, Any]):
        """ایندکس کردن یک سند"""
        self._documents[doc_id] = content

        text = " ".join(str(v) for v in content.values())
        words = self._extract_words(text)

        for word in words:
            if word not in self._index:
                self._index[word] = set()
            self._index[word].add(doc_id)

    def index_bulk(self, documents: Dict[str, Dict[str, Any]]):
        """ایندکس کردن چند سند"""
        for doc_id, content in documents.items():
            self.index_document(doc_id, content)
        logger.info(f"📚 {len(documents)} documents indexed")

    def search(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 20,
        min_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        جستجو در مستندات

        Args:
            query: عبارت جستجو
            fields: فیلدهای جستجو (اختیاری)
            limit: تعداد نتایج
            min_score: حداقل امتیاز

        Returns:
            List[Dict]: نتایج جستجو
        """
        query_words = self._extract_words(query)

        if not query_words:
            return []

        scores = {}

        for doc_id, content in self._documents.items():
            score = self._calculate_score(query_words, content, fields)
            if score >= min_score:
                scores[doc_id] = score

        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in sorted_results[:limit]:
            result = self._documents[doc_id].copy()
            result["_score"] = score
            result["_id"] = doc_id
            results.append(result)

        return results

    def _calculate_score(
        self,
        query_words: List[str],
        content: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> float:
        if fields is None:
            fields = list(content.keys())

        text = ""
        for field in fields:
            if field in content:
                text += f" {content[field]}"

        words = self._extract_words(text)

        if not words:
            return 0

        tf = {}
        for word in words:
            tf[word] = tf.get(word, 0) + 1

        total_score = 0
        for query_word in query_words:
            if query_word in tf:
                score = tf[query_word] / len(words)
                total_score += score
            else:
                for word in words:
                    similarity = SequenceMatcher(None, query_word, word).ratio()
                    if similarity > 0.7:
                        total_score += similarity * 0.5

        return min(total_score / len(query_words), 1.0)

    def _extract_words(self, text: str) -> List[str]:
        if not text:
            return []

        cleaned = re.sub(r'[^\w\s]', ' ', str(text))
        words = cleaned.split()

        return list({w.lower() for w in words if len(w) > 2})

    def clear(self):
        self._index.clear()
        self._documents.clear()
        logger.info("🗑️ Search index cleared")


_search_engine = None


def get_search_engine() -> SearchEngine:
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine


def get_search() -> SearchEngine:
    return get_search_engine()
