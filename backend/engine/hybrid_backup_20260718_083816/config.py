#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/config.py
-------------------------------------------------------
تنها محل تعریف مسیر دیتابیس و تنظیمات مشترک برای کل
engine/hybrid. هیچ فایل دیگری نباید مسیر دیتابیس را خودش
با sqlite3.connect("...") هارد-کد کند؛ همه باید از این‌جا
import کنند.

ساختار فرض‌شده پروژه:
    development/
    ├── data/
    │   └── hdp_v2.db
    └── engine/
        └── hybrid/
            └── config.py   ← همین فایل

اگر مسیر واقعی دیتابیس در پروژه شما فرق دارد، فقط همین یک
خط (DB_PATH) را عوض کنید؛ بقیه فایل‌ها نیازی به تغییر ندارند.
-------------------------------------------------------
"""

from pathlib import Path
import os

# engine/hybrid/config.py -> parents[0]=hybrid, parents[1]=engine, parents[2]=development (ریشه پروژه)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# امکان override از طریق متغیر محیطی، برای تست یا اجرای موقت
# روی مسیر دیگر، بدون دست‌زدن به کد:
#   HDP_DB_PATH=/tmp/test.db python3 hybrid_engine.py ...
_ENV_OVERRIDE = os.environ.get("HDP_DB_PATH")


class HybridConfig:
    DB_PATH: str = _ENV_OVERRIDE or str(PROJECT_ROOT / "data" / "hdp_v2.db")

    # اگر پروژه چند دیتابیس مجزا دارد، همین‌جا اضافه شود:
    # DB_GRAPH = str(PROJECT_ROOT / "data" / "graph.db")
    # DB_GEO   = str(PROJECT_ROOT / "data" / "geo.db")

    CACHE_SIZE: int = 500
    CACHE_TTL: int = 300  # ثانیه

    DEFAULT_TOP_K: int = 10
    EMBEDDING_TABLE: str = "embeddings"
    EMBEDDING_MODEL_DEFAULT = "fallback"
    GRAPH_DEPTH: int = 2
    GRAPH_DECAY: float = 0.6

    LOW_CONFIDENCE_THRESHOLD: float = 0.15
    RRF_K: int = 60

    HYBRID_WEIGHTS = {"keyword": 0.55, "graph": 0.25, "vector": 0.20}

    COMPRESSION_LEVEL: int = 6

    @classmethod
    def ensure_data_dir(cls) -> None:
        """اطمینان از وجود پوشه data قبل از هر اتصال به دیتابیس."""
        Path(cls.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def info(cls) -> dict:
        return {
            "project_root": str(PROJECT_ROOT),
            "db_path": cls.DB_PATH,
            "db_exists": Path(cls.DB_PATH).exists(),
        }


if __name__ == "__main__":
    import json

    print(json.dumps(HybridConfig.info(), ensure_ascii=False, indent=2))
