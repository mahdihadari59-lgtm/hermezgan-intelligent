#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/utils.py
-------------------------------------------------------
ابزارهای عمومی مشترک بین همه فایل‌های engine/hybrid.

نسخه مرجع normalize_persian این‌جاست. graph_builder.py هم
یک نسخه محلی دارد (برای سازگاری با فایل‌های قبلی که مستقیم
از آن import می‌کنند)؛ اگر این دو در آینده واگرا شدند، این
فایل باید منبع حقیقت باشد و graph_builder باید از همین‌جا
import کند، نه برعکس.
-------------------------------------------------------
"""

import re
import unicodedata
import time
import json
from typing import Optional, List, Any


_FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")
_NON_TEXT_RE = re.compile(r"[^\u0600-\u06FF\u0750-\u077Fa-zA-Z0-9\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_persian(text: Optional[str]) -> str:
    """نسخه مرجع نرمال‌سازی متن فارسی (NFKD، حذف نیم‌فاصله، یکسان‌سازی حروف)."""
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = t.replace("\u200c", " ")
    t = t.replace("ي", "ی").replace("ى", "ی")
    t = t.replace("ك", "ک")
    t = t.replace("ۀ", "ه").replace("ة", "ه")
    for ch in "إأآا":
        t = t.replace(ch, "ا")
    t = t.replace("ؤ", "و").replace("ئ", "ی")
    t = _DIACRITICS_RE.sub("", t)
    for i, d in enumerate(_FA_DIGITS):
        t = t.replace(d, str(i))
    for i, d in enumerate(_AR_DIGITS):
        t = t.replace(d, str(i))
    t = _NON_TEXT_RE.sub(" ", t)
    t = _MULTI_SPACE_RE.sub(" ", t).strip()
    return t.lower()


def tokenize(normalized_text: str) -> List[str]:
    if not normalized_text:
        return []
    return [tok for tok in normalized_text.split(" ") if tok]


def now_str() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def chunked(items: List[Any], size: int):
    """تقسیم یک لیست به بخش‌های size تایی — برای INSERTهای دسته‌ای بزرگ."""
    for i in range(0, len(items), size):
        yield items[i : i + size]


def safe_json_loads(raw: Optional[str], default: Any = None) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
