import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
import logging

from app.models.chat import ChatIntent, ChatEntity

logger = logging.getLogger(__name__)


class NLPService:
    """سرویس پردازش زبان طبیعی"""

    def __init__(self, db: Session):
        self.db = db
        self.intent_cache = {}
        self.entity_cache = {}
        self._load_cache()

    def _load_cache(self):
        """بارگذاری کش از دیتابیس"""
        try:
            intents = self.db.query(ChatIntent).filter(ChatIntent.is_active == True).all()
            self.intent_cache = {intent.name: intent for intent in intents}

            entities = self.db.query(ChatEntity).all()
            for entity in entities:
                if entity.synonyms:
                    for synonym in entity.synonyms:
                        self.entity_cache[synonym.lower()] = entity
        except Exception as e:
            logger.error(f"❌ خطا در بارگذاری کش NLP: {e}")

    def reload_cache(self):
        """بارگذاری مجدد کش"""
        self._load_cache()
        logger.info("🔄 کش NLP بارگذاری مجدد شد")

    def detect_intent(self, message: str) -> Tuple[str, float]:
        """
        تشخیص نیت از پیام

        Args:
            message: متن پیام

        Returns:
            Tuple[str, float]: (نام نیت, دقت)
        """
        message = message.lower().strip()

        intent_scores = {}

        for intent_name, intent in self.intent_cache.items():
            score = 0
            keywords = intent.keywords or []

            for keyword in keywords:
                if keyword.lower() in message:
                    score += 1

            # بررسی شباهت
            if score == 0:
                for keyword in keywords:
                    similarity = self.similarity(message, keyword.lower())
                    if similarity > 0.7:
                        score += similarity

            if score > 0:
                intent_scores[intent_name] = score

        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent] / 3, 1.0)
            return best_intent, confidence

        return "general", 0.3

    def extract_entities(self, message: str) -> List[Dict]:
        """
        استخراج موجودیت‌ها از پیام

        Args:
            message: متن پیام

        Returns:
            List[Dict]: لیست موجودیت‌ها
        """
        entities = []
        message_lower = message.lower()

        for synonym, entity in self.entity_cache.items():
            if synonym in message_lower:
                entities.append({
                    "name": entity.name,
                    "type": entity.entity_type,
                    "synonym": synonym,
                    "service_id": entity.service_id,
                    "metadata": entity.metadata
                })

        return entities

    def similarity(self, a: str, b: str) -> float:
        """
        محاسبه شباهت بین دو متن

        Args:
            a: متن اول
            b: متن دوم

        Returns:
            float: میزان شباهت (0 تا 1)
        """
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def extract_keywords(self, text: str) -> List[str]:
        """
        استخراج کلمات کلیدی از متن

        Args:
            text: متن

        Returns:
            List[str]: کلمات کلیدی
        """
        # حذف کاراکترهای خاص
        cleaned = re.sub(r'[^\w\s]', ' ', text)
        words = cleaned.split()

        # حذف کلمات تکراری و کوتاه
        keywords = [w for w in set(words) if len(w) > 2]

        return keywords

    def tokenize_persian(self, text: str) -> List[str]:
        """
        توکن‌سازی متن فارسی

        Args:
            text: متن فارسی

        Returns:
            List[str]: توکن‌ها
        """
        # استفاده از کتابخانه Hazm برای توکن‌سازی دقیق‌تر
        try:
            from hazm import word_tokenize
            return word_tokenize(text)
        except ImportError:
            # Fallback ساده
            return text.split()

    def normalize_persian(self, text: str) -> str:
        """
        نرمال‌سازی متن فارسی

        Args:
            text: متن فارسی

        Returns:
            str: متن نرمال‌سازی شده
        """
        # تبدیل حروف عربی به فارسی
        arabic_to_persian = {
            'ي': 'ی',
            'ك': 'ک',
            'ة': 'ه',
            'أ': 'ا',
            'إ': 'ا',
            'آ': 'ا',
        }

        for arabic, persian in arabic_to_persian.items():
            text = text.replace(arabic, persian)

        # حذف فاصله‌های اضافی
        text = ' '.join(text.split())

        return text

    def extract_location(self, text: str) -> Optional[Dict]:
        """
        استخراج موقعیت مکانی از متن

        Args:
            text: متن

        Returns:
            Optional[Dict]: اطلاعات موقعیت
        """
        from app.core.constants import REGIONS

        text_lower = text.lower()

        for region_id, region_data in REGIONS.items():
            if region_data['name'] in text_lower:
                return {
                    "region_id": region_id,
                    "name": region_data['name'],
                    "center": region_data['center']
                }

        # الگوی مختصات
        coord_pattern = r'(\d+\.\d+)[,\s]+(\d+\.\d+)'
        match = re.search(coord_pattern, text)
        if match:
            try:
                lat = float(match.group(1))
                lng = float(match.group(2))
                return {
                    "region_id": "custom",
                    "latitude": lat,
                    "longitude": lng
                }
            except ValueError:
                pass

        return None
