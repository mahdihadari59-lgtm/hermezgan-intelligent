from __future__ import annotations

import os
from pathlib import Path

try:
    from app.core.config.settings import Settings
    settings = Settings()
except Exception:
    class _FallbackSettings:
        def __getattr__(self, name):
            return None
    settings = _FallbackSettings()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_DB = PROJECT_ROOT / "data" / "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"
HDP_KNOWLEDGE_DB_PATH = PROJECT_ROOT / "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"

DEFAULT_BANDARI_URL = os.getenv("BANDARI_ENGINE_URL", "http://127.0.0.1:5200")
