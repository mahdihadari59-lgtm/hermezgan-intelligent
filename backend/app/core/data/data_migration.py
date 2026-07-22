from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DataMigration:
    """
    کلاس مدیریت مهاجرت داده‌ها
    """

    def __init__(self):
        self.migrations = {}
        self.migration_dir = Path("data/migrations")
        self.migration_dir.mkdir(parents=True, exist_ok=True)

    def register_migration(self, version: str, migration_func: Callable, description: str = ""):
        self.migrations[version] = {
            "func": migration_func,
            "description": description,
            "registered_at": datetime.utcnow().isoformat()
        }
        logger.info(f"✅ Migration registered: v{version}")

    def migrate(self, data: List[Dict[str, Any]], from_version: str, to_version: str) -> List[Dict[str, Any]]:
        if from_version == to_version:
            return data

        versions = sorted(self.migrations.keys())
        if from_version not in versions or to_version not in versions:
            logger.error(f"❌ Version not found: {from_version} or {to_version}")
            return data

        from_idx = versions.index(from_version)
        to_idx = versions.index(to_version)
        result = data

        if from_idx < to_idx:
            for i in range(from_idx + 1, to_idx + 1):
                version = versions[i]
                logger.info(f"🔄 Applying migration to v{version}")
                result = self.migrations[version]["func"](result)
        else:
            for i in range(from_idx, to_idx, -1):
                version = versions[i]
                logger.info(f"🔄 Rolling back migration from v{version}")
                result = self.migrations[version]["func"](result)

        return result

    def save_migration_state(self, version: str, data: List[Dict]):
        file_path = self.migration_dir / f"state_v{version}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Migration state saved: v{version}")

    def load_migration_state(self, version: str) -> List[Dict]:
        file_path = self.migration_dir / f"state_v{version}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


_data_migration = None


def get_data_migration() -> DataMigration:
    global _data_migration
    if _data_migration is None:
        _data_migration = DataMigration()
    return _data_migration
