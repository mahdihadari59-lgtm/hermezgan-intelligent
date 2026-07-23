import re
import hashlib
from typing import List, Dict, Optional, Tuple, Any

class FarsiNLPEngine:
    def __init__(self):
        self.initialized = True
        self._embeddings_cache = {}

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        text = text.replace('ي', 'ی').replace('ك', 'ک')
        return text

    def tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        tokens = self.normalize(text).split()
        tokens = [t.rstrip(':') for t in tokens]
        return tokens

    def lemmatize(self, tokens: List[str]) -> List[str]:
        suffixes = ['ها', 'های', 'تر', 'ترین', 'ی', 'ای', 'ات']
        result = []
        for token in tokens:
            for suffix in suffixes:
                if token.endswith(suffix):
                    token = token[:-len(suffix)]
                    break
            result.append(token)
        return result

    def classify_intent(self, text: str) -> Tuple[str, float]:
        text = self.normalize(text.lower())
        
        # کلمات کلیدی برای هر نیت
        keywords = {
            "greeting": ["سلام", "درود", "هی", "خوبی", "چطوری"],
            "hospital": ["بیمارستان", "بیمار", "درمان", "داکتر", "پزشک", "اورژانس"],
            "restaurant": ["رستوران", "غذا", "کباب", "شام", "ناهار", "کافه"],
            "taxi": ["تاکسی", "خودرو", "رفتن", "اسنپ", "تپسی", "مسافر"],
            "location_query": ["کجا", "نزدیک", "فاصله", "موقعیت", "مکان", "آدرس", "محله", "منطقه", "شهر"],
            "direction": ["راه", "مسیر", "چگونه", "بروم", "رسیدن", "رفتن به", "هدایت", "مسیریابی", "نقشه"]
        }
        
        scores = {intent: 0 for intent in keywords}
        for intent, words in keywords.items():
            for word in words:
                if word in text:
                    scores[intent] += 1
        
        # اولویت‌بندی: اگر کلمات مکان و مسیر با هم باشند
        if scores["direction"] > 0 and scores["location_query"] > 0:
            scores["direction"] += 2  # اولویت direction
        
        # اگر "کجا" با "بیمارستان" باشد، location_query اولویت دارد
        if "کجا" in text and "بیمارستان" in text:
            scores["location_query"] += 3
            scores["hospital"] -= 1
        
        # اگر "راه" یا "مسیر" در متن باشد، direction اولویت دارد
        if any(w in text for w in ["راه", "مسیر", "چگونه بروم"]):
            scores["direction"] += 2
        
        best = max(scores, key=scores.get)
        max_score = scores[best]
        confidence = min(max_score / 3, 1.0) if max_score > 0 else 0.1
        
        return best, confidence

    def get_embeddings(self, text: str) -> List[float]:
        if text in self._embeddings_cache:
            return self._embeddings_cache[text]
        hash_bytes = hashlib.md5(text.encode()).digest()
        embedding = [float(b) / 255.0 for b in hash_bytes]
        embedding = embedding[:32] + [0.0] * (32 - len(embedding))
        self._embeddings_cache[text] = embedding
        return embedding

    def process(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "original_text": text,
                "normalized": "",
                "normalized_text": "",
                "tokens": [],
                "lemmas": [],
                "intent": "unknown",
                "confidence": 0.0,
                "intent_confidence": 0.0,
                "entities": []
            }
        normalized = self.normalize(text)
        tokens = self.tokenize(normalized)
        lemmas = self.lemmatize(tokens)
        intent, confidence = self.classify_intent(text)
        return {
            "original_text": text,
            "normalized": normalized,
            "normalized_text": normalized,
            "tokens": tokens,
            "lemmas": lemmas,
            "intent": intent,
            "confidence": confidence,
            "intent_confidence": confidence,
            "entities": []
        }


_nlp_instance = None

def get_nlp_engine() -> FarsiNLPEngine:
    global _nlp_instance
    if _nlp_instance is None:
        _nlp_instance = FarsiNLPEngine()
    return _nlp_instance
