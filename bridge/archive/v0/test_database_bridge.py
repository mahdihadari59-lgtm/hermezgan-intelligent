import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo.migrate import migrate
from geo.database_bridge import DatabaseBridge, DatabaseBridgeError

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "geo", "schema.sql")


def _make_knowledge_db(path):
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE knowledge (id INTEGER PRIMARY KEY, title TEXT, content TEXT);
        CREATE TABLE knowledge_relations (
            source_entity TEXT, target_entity TEXT, relation_type TEXT, weight INTEGER
        );
        INSERT INTO knowledge_relations VALUES
            ('hospital:Test Hospital', 'street:Test Street', 'co_occurrence', 3);
        """
    )
    conn.commit()
    conn.close()


class DatabaseBridgeTestCase(unittest.TestCase):
    def setUp(self):
        self.geo_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.geo_db.close()
        migrate(self.geo_db.name, SCHEMA)

        self.kdb = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.kdb.close()
        _make_knowledge_db(self.kdb.name)

    def tearDown(self):
        os.unlink(self.geo_db.name)
        os.unlink(self.kdb.name)

    def test_attach_exposes_both_schemas(self):
        with DatabaseBridge(self.geo_db.name, self.kdb.name) as bridge:
            names = {s["name"] for s in bridge.list_schemas()}
            self.assertEqual(names, {"main", "knowledge"})

    def test_neither_database_is_modified_by_attaching(self):
        geo_tables_before = set(sqlite3.connect(self.geo_db.name).execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall())
        with DatabaseBridge(self.geo_db.name, self.kdb.name):
            pass
        geo_tables_after = set(sqlite3.connect(self.geo_db.name).execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall())
        self.assertEqual(geo_tables_before, geo_tables_after)

    def test_cross_database_join(self):
        with DatabaseBridge(self.geo_db.name, self.kdb.name) as bridge:
            bridge._conn.execute(
                "INSERT INTO hospitals (name, lat, lng, type) VALUES (?, ?, ?, ?)",
                ("Test Hospital", 27.2, 56.2, "general"),
            )
            bridge._conn.commit()
            rows = bridge.query(
                """
                SELECT h.name, r.target_entity, r.weight
                FROM hospitals h
                JOIN knowledge.knowledge_relations r ON r.source_entity = 'hospital:' || h.name
                """
            )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["target_entity"], "street:Test Street")

    def test_detach_removes_knowledge_schema(self):
        bridge = DatabaseBridge(self.geo_db.name, self.kdb.name)
        bridge.connect()
        bridge.detach()
        names = {s["name"] for s in bridge.list_schemas()}
        self.assertEqual(names, {"main"})
        bridge.close()

    def test_invalid_alias_rejected(self):
        with self.assertRaises(DatabaseBridgeError):
            DatabaseBridge(self.geo_db.name, self.kdb.name, knowledge_alias="bad; DROP TABLE x")

    def test_missing_knowledge_db_raises_bridge_error(self):
        bridge = DatabaseBridge(self.geo_db.name, "/definitely/not/a/real/path.db")
        with self.assertRaises(DatabaseBridgeError):
            bridge.connect()

    def test_close_is_idempotent(self):
        bridge = DatabaseBridge(self.geo_db.name, self.kdb.name)
        bridge.connect()
        bridge.close()
        bridge.close()  # should not raise


if __name__ == "__main__":
    unittest.main()
