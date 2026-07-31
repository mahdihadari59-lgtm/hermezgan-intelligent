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
DEFAULT_KNOWLEDGE_DB = PROJECT_ROOT / "data" / "hdp_v2.db"
HDP_KNOWLEDGE_DB_PATH = Path("/data/data/com.termux/files/home/hermezgan-intelligent-backup-20260729/backend/archive/backups/knowledge_geo_populate_20260728_194944/hdp_v2_embedding_ok.db")

DEFAULT_BANDARI_URL = os.getenv("BANDARI_ENGINE_URL", "http://127.0.0.1:5200/api")
