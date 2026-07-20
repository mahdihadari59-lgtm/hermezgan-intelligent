#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/compressor.py
-------------------------------------------------------
فشرده‌سازی سبک برای متن و بردارها، با zlib استاندارد پایتون
(بدون هیچ وابستگی خارجی). هدف: کاهش حجم دیتابیس روی
حافظه محدود موبایل/Termux، مخصوصاً برای content طولانی نودها
یا بردارهای TF-IDF با ابعاد بالا.

نکته: فقط برای داده‌هایی که به‌ندرت خوانده می‌شوند (مثلا content
آرشیوی) استفاده شود؛ فشرده‌سازی/باز کردن هزینه CPU دارد و برای
مسیرهای پرتکرار جستجو (hot path) مناسب نیست.
-------------------------------------------------------
"""

import zlib
import json
import base64
from typing import Any

from engine.hybrid.config import HybridConfig


def compress_text(text: str, level: int = None) -> bytes:
    level = level if level is not None else HybridConfig.COMPRESSION_LEVEL
    return zlib.compress(text.encode("utf-8"), level)


def decompress_text(data: bytes) -> str:
    return zlib.decompress(data).decode("utf-8")


def compress_json(obj: Any, level: int = 6) -> bytes:
    raw = json.dumps(obj, ensure_ascii=False)
    return zlib.compress(raw.encode("utf-8"), level)


def decompress_json(data: bytes) -> Any:
    raw = zlib.decompress(data).decode("utf-8")
    return json.loads(raw)


def compress_to_b64(text: str, level: int = 6) -> str:
    """برای مواقعی که باید نتیجه فشرده در یک ستون TEXT (نه BLOB) ذخیره شود."""
    compressed = zlib.compress(text.encode("utf-8"), level)
    return base64.b64encode(compressed).decode("ascii")


def decompress_from_b64(b64_text: str) -> str:
    compressed = base64.b64decode(b64_text.encode("ascii"))
    return zlib.decompress(compressed).decode("utf-8")


def compression_ratio(original: str, compressed: bytes) -> float:
    original_size = len(original.encode("utf-8"))
    if original_size == 0:
        return 0.0
    return round(1 - (len(compressed) / original_size), 3)
