"""
SQLite3 Connector - connects to user's existing HDP database
"""
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from src.utils.config import DB_PATH

class HdpDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_fts()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: tuple = ()) -> int:
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid

    def _ensure_fts(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_pois USING fts5(
                    name_fa, category, keywords,
                    content=pois, content_rowid=rowid
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_tourism USING fts5(
                    name_fa, description_fa, keywords, city,
                    content=tourism_poi, content_rowid=rowid
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS fts_business USING fts5(
                    name, category, subcategory, city, neighborhood,
                    content=markets, content_rowid=rowid
                )
            """)
            conn.commit()

    def get_table_counts(self) -> Dict[str, int]:
        tables = [
            "roads", "pois", "markets", "rag_embeddings", "offices", "cities",
            "transport", "restaurants", "bandari_vocabulary_master", "parks",
            "neighborhoods", "healthcare", "hotels", "poi_descriptions",
            "documents", "graph_nodes_master", "cafes", "education",
            "pharmacies", "tourism_poi", "fuel_stations", "banks",
            "universities", "graph_entities_master", "sources", "routes",
            "shopping_centers", "urban_areas", "natural_attractions",
            "cameras_atlas", "traffic_data", "accident_hotspots",
            "alternative_routes", "hotspots_info", "public_schools",
            "tourism_activities", "tourism_food", "graph_relation_types_master",
            "religious_sites", "industries", "knowledge", "cultural_sites",
            "medical_centers", "souvenir_shops", "traffic_info",
            "educational_centers", "traffic_devices", "bandari_phrases_master",
            "private_schools", "tourist_areas", "parking_lots", "tourism_events",
            "bridges", "cameras_info", "realtime_traffic", "graph_relations_master"
        ]
        counts = {}
        with self._connect() as conn:
            for t in tables:
                try:
                    row = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()
                    counts[t] = row[0]
                except Exception:
                    counts[t] = 0
        return counts

    def search_pois(self, q: str, limit: int = 10) -> List[Dict]:
        sql = """
            SELECT p.* FROM pois p
            JOIN fts_pois f ON p.rowid = f.rowid
            WHERE fts_pois MATCH ? ORDER BY rank LIMIT ?
        """
        return self.query(sql, (q, limit))

    def search_tourism(self, q: str, limit: int = 10) -> List[Dict]:
        sql = """
            SELECT t.* FROM tourism_poi t
            JOIN fts_tourism f ON t.rowid = f.rowid
            WHERE fts_tourism MATCH ? ORDER BY rank LIMIT ?
        """
        return self.query(sql, (q, limit))

    def search_business(self, q: str, limit: int = 10) -> List[Dict]:
        sql = """
            SELECT m.* FROM markets m
            JOIN fts_business f ON m.rowid = f.rowid
            WHERE fts_business MATCH ? ORDER BY rank LIMIT ?
        """
        return self.query(sql, (q, limit))

db = HdpDatabase()
