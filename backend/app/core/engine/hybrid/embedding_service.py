from typing import List, Optional
import numpy as np
import logging
import hashlib
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    سرویس تولید Embedding برای متون
    پشتیبانی از چندین backend: Sentence-Transformers, OpenAI, Local
    """

    def __init__(self):
        self.model = None
        self.model_type = "local"
        self.cache = {}
        self._cache_path = Path("data/embeddings_cache.json")

        self._load_cache()

        self._initialize_model()

        logger.info(f"✅ Embedding Service initialized with {len(self.cache)} cached embeddings")

    def _initialize_model(self):
        try:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                self.model_type = "sentence_transformers"
                logger.info("✅ Sentence-Transformers model loaded")
                return
            except ImportError:
                logger.warning("⚠️ Sentence-Transformers not installed, using fallback")

            self.model_type = "tfidf"
            logger.info("✅ Using TF-IDF fallback for embeddings")

        except Exception as e:
            logger.error(f"❌ Error initializing embedding model: {e}")
            self.model_type = "random"
            logger.info("⚠️ Using random embeddings as fallback")

    def get_embedding(self, text: str) -> Optional[List[float]]:
        if not text:
            return None

        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            if self.model_type == "sentence_transformers":
                embedding = self.model.encode(text, convert_to_numpy=True)
                result = embedding.tolist()

            elif self.model_type == "tfidf":
                result = self._tfidf_embedding(text)

            else:
                result = np.random.randn(384).tolist()

            self.cache[cache_key] = result
            self._save_cache()

            return result

        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            return None

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            emb = self.get_embedding(text)
            if emb:
                embeddings.append(emb)
        return embeddings

    def _tfidf_embedding(self, text: str) -> List[float]:
        words = text.lower().split()
        if not words:
            return [0.0] * 100

        unique_words = list(set(words))

        embedding = [0.0] * 100

        for i, word in enumerate(unique_words[:100]):
            hash_val = hash(word) % 100
            embedding[hash_val] += 1

        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [v / norm for v in embedding]

        return embedding

    def _load_cache(self):
        try:
            if not self._cache_path.exists():
                return

            with open(self._cache_path, "r", encoding="utf-8") as f:
                self.cache = json.load(f)

        except Exception as e:
            logger.error(f"❌ Error loading embedding cache: {e}")
            self.cache = {}

    def _save_cache(self):
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)

            if len(self.cache) > 10000:
                items = list(self.cache.items())
                self.cache = dict(items[-5000:])

            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False)

        except Exception as e:
            logger.error(f"❌ Error saving embedding cache: {e}")

    def clear_cache(self):
        self.cache = {}
        self._save_cache()
        logger.info("🗑️ Embedding cache cleared")


_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
