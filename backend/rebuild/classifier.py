# classifier.py (با متد کمکی classify_record)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Knowledge Classifier
موتور طبقه‌بندی دانش برای پروژه هرمزگان هوشمند
"""

from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class KnowledgeRecord:
    """رکورد دانش با فیلدهای طبقه‌بندی"""
    title: str = ""
    content: str = ""
    category: str = "general"
    city: str = ""
    entity_type: str = "knowledge"
    intent: str = "knowledge"
    main_intent: str = "knowledge"
    sub_intent: str = "general"
    topic: str = "general"
    confidence: float = 0.0
    source: str = "osm"
    metadata: Dict = field(default_factory=dict)


class KnowledgeClassifier:
    """
    موتور طبقه‌بندی دانش با سیستم Rule-Based و امتیازدهی
    """

    # قوانین دسته‌بندی (مشابه نسخه قبل)
    CATEGORY_RULES = {
        "traffic": ["ترافیک", "چهارراه", "بلوار", "میدان", "چراغ", "دوربین", "سرعت", "تصادف", "حادثه", "جاده", "محور", "راه", "خیابان", "تونل", "پل"],
        "tourism": ["جزیره", "ساحل", "گردشگری", "تفریحی", "هتل", "اقامت", "جاذبه", "پارک", "تفریح", "بازار", "سوغات"],
        "medical": ["بیمارستان", "پزشک", "دارو", "بیمار", "اورژانس", "درمان", "سلامت", "کلینیک", "درمانگاه", "داروخانه"],
        "food": ["غذا", "رستوران", "کافه", "فست‌فود", "قلیه", "هواری", "مهیاوه", "رنگینک", "کلمبه", "نان"],
        "government": ["شهرداری", "فرمانداری", "اداره", "سازمان", "استانداری", "وزارت", "دولت", "شورا"],
        "geography": ["هرمزگان", "بندرعباس", "میناب", "قشم", "کیش", "جاسک", "حاجی‌آباد", "رودان", "بستک", "سیریک", "خمیر", "بندرلنگه", "پارسیان", "بشاگرد", "ابوموسی", "تنب"],
        "education": ["مدرسه", "دانشگاه", "دانش‌آموز", "دانشجو", "آموزش", "کلاس", "معلم", "استاد", "کتابخانه", "آموزشگاه"],
        "economy": ["اقتصاد", "کسب‌وکار", "بازار", "تولید", "صادرات", "واردات", "بندر", "کشتی", "کالا", "تجارت"],
        "culture": ["فرهنگ", "تاریخ", "هنر", "میراث", "سنتی", "آداب", "رسوم", "جشن", "مراسم", "لهجه", "گویش", "فولکلور"],
    }

    CITY_RULES = ["بندرعباس", "قشم", "کیش", "میناب", "بندرلنگه", "پارسیان", "جاسک", "رودان", "حاجی‌آباد", "بستک", "سیریک", "بشاگرد", "خمیر", "ابوموسی", "تنب بزرگ", "تنب کوچک"]

    ENTITY_RULES = {
        "province": ["استان", "هرمزگان"],
        "city": ["شهر", "بندرعباس", "قشم", "کیش"],
        "intersection": ["چهارراه", "میدان", "تقاطع", "سه‌راه"],
        "hospital": ["بیمارستان", "درمانگاه", "کلینیک"],
        "hotel": ["هتل", "مسافرخانه", "اقامتگاه"],
        "restaurant": ["رستوران", "کافه", "غذاخوری"],
        "island": ["جزیره", "قشم", "کیش", "هرمز"],
        "road": ["جاده", "بلوار", "محور", "خیابان"],
        "school": ["مدرسه", "آموزشگاه", "هنرستان"],
        "university": ["دانشگاه", "مرکز آموزش", "دانشکده"],
        "park": ["پارک", "بوستان", "فضای سبز"],
        "museum": ["موزه", "خانه تاریخی", "کاخ"],
        "market": ["بازار", "مرکز خرید", "مجتمع تجاری"],
    }

    INTENT_RULES = {
        "traffic_status": ["ترافیک", "تصادف", "سرعت", "راهبندان", "حادثه", "تخلف", "جریمه"],
        "tourism_info": ["گردشگری", "جزیره", "ساحل", "تفریح", "هتل", "اقامت", "جاذبه", "تور", "سوغات"],
        "medical_info": ["بیمارستان", "درمان", "پزشک", "بیمار", "دارو", "اورژانس", "کلینیک", "سلامت"],
        "food_recipe": ["مواد لازم", "دستور پخت", "طرز تهیه", "غذا", "خوشمزه", "سنتی", "محلی"],
        "introduce_location": ["معرفی", "آشنایی با", "شناخت", "اطلاعات کلی", "توضیح درباره"],
        "educational_info": ["مدرسه", "دانشگاه", "آموزش", "دانش‌آموز", "دانشجو", "کلاس", "معلم", "استاد"],
        "economic_info": ["اقتصاد", "بازار", "کسب‌وکار", "صادرات", "واردات", "کشتی", "بندر", "تجارت"],
        "cultural_info": ["فرهنگ", "تاریخ", "هنر", "میراث", "سنتی", "آداب", "رسوم", "فولکلور"],
        "geography_info": ["جغرافیا", "موقعیت", "آب‌وهوا", "اقلیم", "کوهستان", "دریا", "بیابان", "طبیعت"],
    }

    PRIORITY_RULES = [
        ("معرفی استان", "geography", "province", "introduce_location"),
        ("معرفی شهر", "geography", "city", "introduce_location"),
        ("معرفی جزیره", "geography", "island", "introduce_location"),
        ("استان هرمزگان", "geography", "province", "geography_info"),
        ("شهرستان", "geography", "city", "geography_info"),
        ("جزیره", "geography", "island", "tourism_info"),
        ("تصادف", "traffic", "road", "traffic_status"),
        ("ترافیک", "traffic", "road", "traffic_status"),
        ("بیمارستان", "medical", "hospital", "medical_info"),
        ("داروخانه", "medical", "pharmacy", "medical_info"),
        ("مدرسه", "education", "school", "educational_info"),
        ("دانشگاه", "education", "university", "educational_info"),
        ("هتل", "tourism", "hotel", "tourism_info"),
        ("رستوران", "food", "restaurant", "food_recipe"),
    ]

    # ==============================================================
    # متدهای اصلی
    # ==============================================================

    def classify(self, record: KnowledgeRecord) -> KnowledgeRecord:
        """طبقه‌بندی کامل یک رکورد دانش"""
        text = f"{record.title} {record.content}"
        title = record.title or ""

        # 1. اولویت: بررسی Priority Rules
        priority_result = self._check_priority(title)
        if priority_result:
            category, entity_type, intent = priority_result
            record.category = category
            record.entity_type = entity_type
            record.intent = intent
            record.main_intent = intent
            record.sub_intent = category
            record.topic = category
            record.confidence = 0.95
        else:
            # 2. سیستم امتیازدهی
            record.category = self.detect_category(text)
            record.entity_type = self.detect_entity(text)
            record.intent = self.detect_intent(text)
            record.main_intent = record.intent
            record.sub_intent = record.category
            record.topic = record.category
            record.confidence = 0.70

        # 3. تشخیص شهر
        record.city = self.detect_city(text)

        return record

    def classify_record(self, title: str, content: str = "") -> KnowledgeRecord:
        """متد کمکی برای طبقه‌بندی با title و content"""
        record = KnowledgeRecord(title=title, content=content)
        return self.classify(record)

    def detect_category(self, text: str) -> str:
        """تشخیص دسته‌بندی با سیستم امتیازدهی"""
        scores = defaultdict(int)
        for category, words in self.CATEGORY_RULES.items():
            for word in words:
                if word in text:
                    scores[category] += 1
        if not scores:
            return "general"
        return max(scores, key=scores.get)

    def detect_city(self, text: str) -> str:
        """تشخیص شهر"""
        for city in self.CITY_RULES:
            if city in text:
                return city
        return ""

    def detect_entity(self, text: str) -> str:
        """تشخیص نوع موجودیت با سیستم امتیازدهی"""
        scores = defaultdict(int)
        for entity, words in self.ENTITY_RULES.items():
            for word in words:
                if word in text:
                    scores[entity] += 1
        if not scores:
            return "knowledge"
        return max(scores, key=scores.get)

    def detect_intent(self, text: str) -> str:
        """تشخیص Intent با سیستم امتیازدهی"""
        scores = defaultdict(int)
        for intent, words in self.INTENT_RULES.items():
            for word in words:
                if word in text:
                    scores[intent] += 1
        if not scores:
            return "knowledge"
        return max(scores, key=scores.get)

    def _check_priority(self, title: str) -> Optional[Tuple[str, str, str]]:
        """بررسی Priority Rules"""
        for pattern, category, entity_type, intent in self.PRIORITY_RULES:
            if pattern in title:
                return (category, entity_type, intent)
        return None

    def get_category_info(self, category: str) -> Dict:
        """دریافت اطلاعات یک دسته‌بندی"""
        info = {
            "traffic": {"name_fa": "ترافیک", "icon": "🚦", "color": "#FF6B6B"},
            "tourism": {"name_fa": "گردشگری", "icon": "🏖️", "color": "#4ECDC4"},
            "medical": {"name_fa": "سلامت", "icon": "🏥", "color": "#FF6B6B"},
            "food": {"name_fa": "غذا", "icon": "🍽️", "color": "#F9CA24"},
            "government": {"name_fa": "دولتی", "icon": "🏛️", "color": "#6C5CE7"},
            "geography": {"name_fa": "جغرافیا", "icon": "🌍", "color": "#00B894"},
            "education": {"name_fa": "آموزش", "icon": "📚", "color": "#FD79A8"},
            "economy": {"name_fa": "اقتصاد", "icon": "💰", "color": "#FDCB6E"},
            "culture": {"name_fa": "فرهنگ", "icon": "🎭", "color": "#A29BFE"},
            "general": {"name_fa": "عمومی", "icon": "📌", "color": "#B2BEC3"},
        }
        return info.get(category, info["general"])

    def get_intent_info(self, intent: str) -> Dict:
        """دریافت اطلاعات یک Intent"""
        info = {
            "traffic_status": {"name_fa": "وضعیت ترافیک"},
            "tourism_info": {"name_fa": "اطلاعات گردشگری"},
            "medical_info": {"name_fa": "اطلاعات پزشکی"},
            "food_recipe": {"name_fa": "دستور پخت"},
            "introduce_location": {"name_fa": "معرفی مکان"},
            "educational_info": {"name_fa": "اطلاعات آموزشی"},
            "economic_info": {"name_fa": "اطلاعات اقتصادی"},
            "cultural_info": {"name_fa": "اطلاعات فرهنگی"},
            "geography_info": {"name_fa": "اطلاعات جغرافیایی"},
            "knowledge": {"name_fa": "دانش عمومی"},
        }
        return info.get(intent, info["knowledge"])
