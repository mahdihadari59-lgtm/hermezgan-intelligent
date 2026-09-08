import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class NLPEngine:
    """
    موتور پردازش زبان طبیعی
    تشخیص نیت، استخراج موجودیت، تحلیل احساسات، نرمال‌سازی متن
    """

    def __init__(self):
        self._intent_patterns = {}
        self._entity_patterns = {}
        self._load_patterns()

    def _load_patterns(self):
        """بارگذاری الگوهای نیت و موجودیت"""
        try:
            self._intent_patterns = {
                "hospital": {
                    "keywords": ["بیمارستان", "بیمار", "درمان", "داکتر", "دکتر", "پزشک", "اورژانس"],
                    "weight": 1.0
                },
                "restaurant": {
                    "keywords": ["رستوران", "غذا", "کباب", "شام", "ناهار", "فست فود", "پیتزا"],
                    "weight": 1.0
                },
                "taxi": {
                    "keywords": ["تاکسی", "خودرو", "رفتن", "حمل", "مسافر", "سوار", "پیاده"],
                    "weight": 1.0
                },
                "camera": {
                    "keywords": ["دوربین", "نظارتی", "تخلف", "سرعت", "ترافیک", "ثبت", "پلاک"],
                    "weight": 1.0
                },
                "hotspot": {
                    "keywords": ["حادثه", "خطرناک", "تصادف", "خطر", "حادثه‌خیز", "مشکل", "بحران"],
                    "weight": 1.0
                },
                "location": {
                    "keywords": ["موقعیت", "مکان", "کجا", "آدرس", "نزدیک", "دور", "فاصله"],
                    "weight": 1.0
                },
                "weather": {
                    "keywords": ["آب و هوا", "هوا", "باران", "گرما", "سرما", "طوفان", "دما"],
                    "weight": 0.8
                },
                "route": {
                    "keywords": ["مسیر", "راه", "رفتن", "رسیدن", "آدرس", "نقشه", "راهنمایی"],
                    "weight": 0.8
                },
                "general": {
                    "keywords": ["سلام", "خوب", "ممنون", "مرسی", "بله", "خیر", "نه"],
                    "weight": 0.5
                }
            }

            self._entity_patterns = {
                "region": {
                    "patterns": [
                        r'(بندرعباس|قشم|کیش|هرمز|میناب|رودان|بستک|بندرلنگه|جاسک)',
                        r'(جزیره\s+(قشم|کیش|هرمز|ابوموسی))',
                        r'(شهرستان\s+(میناب|رودان|بستک|بندرلنگه|جاسک|حاجی‌آباد|بشاگرد|خمیر|سیریک))'
                    ]
                },
                "service": {
                    "patterns": [
                        r'(بیمارستان\s+[\w\s]+)',
                        r'(رستوران\s+[\w\s]+)',
                        r'(داروخانه\s+[\w\s]+)',
                        r'(مدرسه\s+[\w\s]+)',
                        r'(تاکسی\s+[\w\s]+)'
                    ]
                },
                "number": {
                    "patterns": [
                        r'(\d+)',
                        r'(\d+\.\d+)'
                    ]
                },
                "time": {
                    "patterns": [
                        r'(\d{1,2}:\d{2})',
                        r'(\d{1,2}\s+(ساعت|دقیقه|ثانیه))'
                    ]
                }
            }

            logger.info("✅ NLP patterns loaded successfully")

        except Exception as e:
            logger.error(f"❌ Error loading NLP patterns: {e}")

    def detect_intent(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        scores = {}

        for intent, data in self._intent_patterns.items():
            score = 0
            keywords = data.get("keywords", [])
            weight = data.get("weight", 1.0)

            for keyword in keywords:
                if keyword in text_lower:
                    score += 1

                for word in text_lower.split():
                    similarity = SequenceMatcher(None, keyword, word).ratio()
                    if similarity > 0.8:
                        score += similarity * 0.5

            max_possible = len(keywords)
            normalized_score = min(score / max_possible * weight, 1.0) if max_possible > 0 else 0

            if normalized_score > 0:
                scores[intent] = normalized_score

        if not scores:
            return "general", 0.3

        best_intent = max(scores, key=scores.get)
        return best_intent, scores[best_intent]

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        entities = []

        for entity_type, patterns in self._entity_patterns.items():
            for pattern in patterns.get("patterns", []):
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        "type": entity_type,
                        "value": match[0] if isinstance(match, tuple) else match
                    })

        return entities

    def normalize_text(self, text: str) -> str:
        if not text:
            return ""

        arabic_to_persian = {
            '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴',
            '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹', '٠': '۰'
        }

        for arabic, persian in arabic_to_persian.items():
            text = text.replace(arabic, persian)

        arabic_to_persian_letters = {
            'ي': 'ی',
            'ك': 'ک',
            'ة': 'ه',
            'أ': 'ا',
            'إ': 'ا',
            'آ': 'ا',
        }

        for arabic, persian in arabic_to_persian_letters.items():
            text = text.replace(arabic, persian)

        text = ' '.join(text.split())

        return text

    def tokenize_persian(self, text: str) -> List[str]:
        try:
            from hazm import word_tokenize
            return word_tokenize(text)
        except ImportError:
            return text.split()

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        positive_words = ["خوب", "عالی", "عشق", "عالی", "عالی", "عالی", "عالی"]
        negative_words = ["بد", "افتضاح", "نفرت", "خسته", "عصبانی"]

        text_lower = text.lower()
        words = text_lower.split()

        positive_score = sum(1 for w in words if w in positive_words)
        negative_score = sum(1 for w in words if w in negative_words)

        total = positive_score + negative_score
        if total == 0:
            return {"positive": 0.5, "negative": 0.5, "neutral": 0.0}

        return {
            "positive": positive_score / total,
            "negative": negative_score / total,
            "neutral": 0.0
        }

    def get_keywords(self, text: str, top_n: int = 10) -> List[str]:
        words = self.tokenize_persian(text)

        word_freq = {}
        for word in words:
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, _ in sorted_words[:top_n]]


_nlp_engine = None


def get_nlp_engine() -> NLPEngine:
    global _nlp_engine
    if _nlp_engine is None:
        _nlp_engine = NLPEngine()
    return _nlp_engine


def get_nlp() -> NLPEngine:
    return get_nlp_engine()
