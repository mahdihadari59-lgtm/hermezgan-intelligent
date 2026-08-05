from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional


_ALLOWED_GEO_TABLES = {
    "cameras",
    "hospitals",
    "fuel_stations",
    "roads",
    "pois",
    "traffic",
}


class GeoRepository:
    def __init__(
        self,
        geo_db_path: Optional[str] = None,
        knowledge_db_path: Optional[str] = None,
    ) -> None:
        backend_root = Path(__file__).resolve().parents[2]

        self.geo_db_path = Path(
            geo_db_path
            or os.getenv("GEO_DB_PATH")
            or backend_root / "geo.db"
        )

        self.knowledge_db_path = Path(
            knowledge_db_path
            or os.getenv("KNOWLEDGE_DB_PATH")
            or os.getenv("HDP_DB_PATH")
            or os.getenv("DATABASE_PATH")
            or backend_root / "hdp_v2_embedding_ok.db"
        )

    @contextmanager
    def _connect(self, path: Path):
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_links_for_knowledge(self, knowledge_id: int) -> List[Dict[str, Any]]:
        if not self.knowledge_db_path.exists():
            return []

        sql = (
            "SELECT id, knowledge_id, geo_table, geo_id, relation_type, confidence, created_at "
            "FROM knowledge_geo_link "
            "WHERE knowledge_id = ? "
            "ORDER BY confidence DESC, created_at DESC, id DESC"
        )

        with self._connect(self.knowledge_db_path) as conn:
            rows = conn.execute(sql, (knowledge_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_geo_entity(self, geo_table: str, geo_id: int) -> Optional[Dict[str, Any]]:
        if geo_table not in _ALLOWED_GEO_TABLES:
            return None

        if not self.geo_db_path.exists():
            return None

        sql = f"SELECT * FROM {geo_table} WHERE id = ? LIMIT 1"

        with self._connect(self.geo_db_path) as conn:
            row = conn.execute(sql, (geo_id,)).fetchone()
            return dict(row) if row else None

    def enrich_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(item, dict):
            return item

        knowledge_id = item.get("knowledge_id")
        if knowledge_id is None:
            return item

        try:
            knowledge_id_int = int(knowledge_id)
        except Exception:
            return item

        links = self.get_links_for_knowledge(knowledge_id_int)
        geo_links: List[Dict[str, Any]] = []

        for link in links:
            geo_table = str(link.get("geo_table", ""))
            geo_id = link.get("geo_id")
            try:
                geo_id_int = int(geo_id)
            except Exception:
                geo_id_int = -1

            geo_entity = self.get_geo_entity(geo_table, geo_id_int)
            geo_links.append(
                {
                    "link": link,
                    "geo_entity": geo_entity,
                }
            )

        item["geo_links"] = geo_links
        return item

    def enrich_payload(self, payload: Any) -> Any:
        if isinstance(payload, dict):
            if "knowledge_id" in payload:
                payload = self.enrich_item(payload)

            for key in ("results", "items", "data", "messages", "records"):
                value = payload.get(key)
                if isinstance(value, list):
                    payload[key] = [self.enrich_payload(v) for v in value]
            return payload

        if isinstance(payload, list):
            return [self.enrich_payload(v) for v in payload]

        return payload


_geo_repo: Optional[GeoRepository] = None


def get_geo_repository() -> GeoRepository:
    global _geo_repo
    if _geo_repo is None:
        _geo_repo = GeoRepository()
    return _geo_repo


def enrich_payload(payload: Any) -> Any:
    try:
        return get_geo_repository().enrich_payload(payload)
    except Exception:
        return payload
