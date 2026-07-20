#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/constants.py
-------------------------------------------------------
مقادیر ثابت مشترک بین همه فایل‌های engine/hybrid و experts/.
هدف: جلوگیری از پخش‌شدن رشته‌های جادویی (magic strings) مثل
اسم دامنه‌ها یا node_typeها در فایل‌های مختلف.

این فایل فقط داده است، نه منطق؛ منطق در config.py و بقیه
ماژول‌ها می‌ماند.
-------------------------------------------------------
"""

# دامنه‌های شناخته‌شده گراف (باید با domain هر graph_node هم‌خوانی داشته باشد)
DOMAINS = [
    "atlas",
    "tourism",
    "traffic",
    "health",
    "food",
    "legal",
    "weather",
    "culture",
    "city",
    "economy",
    "education",
    "employment",
    "technology",
    "auto",
    "general",
]

# انواع نود رایج در گراف (node_type) — برای استفاده در node_features/edge_builder
NODE_TYPES = [
    "incident",     # رویداد/حادثه (مثلا تصادف)
    "status",       # وضعیت لحظه‌ای (مثلا وضعیت ترافیک)
    "service",      # خدمت (مثلا داروخانه)
    "facility",     # مکان/تاسیسات (مثلا بیمارستان)
    "attraction",   # جاذبه گردشگری
    "generic",      # پیش‌فرض/نامشخص
]

# نگاشت expert_id -> دامنه‌ها (نسخه مرجع؛ هم در knowledge-search.py
# قدیمی و هم در hybrid_engine.py استفاده می‌شود — اینجا یکجا نگه
# داشته می‌شود تا هر دو از یک منبع بخوانند)
# نگاشت expert_id -> دامنه‌ها. عمداً خالی گذاشته شده — طبق تصمیم
# پروژه، این نگاشت دیگر این‌جا هارد-کد نمی‌شود؛ باید در زمان اجرا
# از دیتابیس واقعی (مثلاً یک جدول expert_domains یا معادلش در
# hdp_v2.db) خوانده و به HybridEngine/BaseExpertEngine تزریق شود.
#
# نتیجه مهم این خالی‌بودن: اگر HybridEngine بدون expert_domain_map
# صریح ساخته بشه، دیگه هیچ فیلتر دامنه‌ای اعمال نمی‌شه (هر Expert
# روی کل گراف جستجو می‌کنه، نه فقط دامنه خودش) — تا وقتی منبع واقعی
# این نگاشت وصل بشه.
EXPERT_DOMAIN_MAP = {}

# آستانه‌های پیش‌فرض (بعضی‌ها هم در config.py تکرار شده‌اند تا هرکدام
# مستقل قابل‌استفاده باشند؛ در صورت تعارض، مقدار config.py حاکم است)
DEFAULT_MIN_SCORE = 0.05
DEFAULT_TOP_K = 10

# نام model های embedding قابل‌استفاده در embedding_storage
EMBEDDING_MODEL_TFIDF = "tfidf"
EMBEDDING_MODEL_FEATURES = "node_features"
EMBEDDING_MODEL_PAGERANK = "pagerank"  # ذخیره امتیاز pagerank هم به‌شکل بردار تک‌بعدی

# نسخه schema گراف — برای migration های آینده
GRAPH_SCHEMA_VERSION = 1
