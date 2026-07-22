from pathlib import Path
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database.session import get_db_session_manager
from app.core.config import settings

logger = logging.getLogger(__name__)


class SeederManager:
    """
    مدیریت Seeders (داده‌های اولیه)
    """

    def __init__(self, seeders_dir: str = "database/seeds"):
        self.seeders_dir = Path(seeders_dir)
        self.seeders_dir.mkdir(parents=True, exist_ok=True)
        self.manager = get_db_session_manager()

    def create_seeder(self, name: str, description: str = "") -> str:
        filename = f"{name}.json"
        file_path = self.seeders_dir / filename

        content = {
            "name": name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "data": {}
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)

        logger.info(f"📝 Seeder created: {file_path}")
        return str(file_path)

    def get_seeders(self) -> List[Dict[str, Any]]:
        seeders = []

        for file_path in sorted(self.seeders_dir.glob("*.json")):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            seeders.append({
                "filename": file_path.name,
                "path": str(file_path),
                "name": data.get("name", file_path.stem),
                "description": data.get("description", ""),
                "created_at": data.get("created_at"),
                "size": file_path.stat().st_size
            })

        return seeders

    def run_seeder(self, seeder_file: str) -> bool:
        file_path = self.seeders_dir / seeder_file

        if not file_path.exists():
            logger.error(f"❌ Seeder file not found: {seeder_file}")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            table_name = data.get("table")
            records = data.get("data", [])

            if not table_name or not records:
                logger.warning(f"⚠️ Seeder has no table or data: {seeder_file}")
                return False

            inspector = inspect(self.manager.engine)
            if table_name not in inspector.get_table_names():
                logger.error(f"❌ Table not found: {table_name}")
                return False

            with self.manager.engine.connect() as conn:
                if data.get("truncate", False):
                    conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

                for record in records:
                    columns = ", ".join(record.keys())
                    placeholders = ", ".join([f":{k}" for k in record.keys()])
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    conn.execute(text(query), record)

                conn.commit()

            logger.info(f"✅ Seeder executed: {seeder_file} ({len(records)} records)")
            return True

        except Exception as e:
            logger.error(f"❌ Error executing seeder: {e}")
            return False

    def run_all_seeders(self) -> int:
        seeders = self.get_seeders()
        executed = 0

        for seeder in seeders:
            if self.run_seeder(seeder["filename"]):
                executed += 1

        return executed


_seeder_manager = None


def get_seeder_manager() -> SeederManager:
    global _seeder_manager
    if _seeder_manager is None:
        _seeder_manager = SeederManager()
    return _seeder_manager


def run_seeders() -> int:
    manager = get_seeder_manager()
    return manager.run_all_seeders()
