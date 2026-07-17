#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Bridge v1 Test Suite

Production validation tests.

Tests:

✓ Connection
✓ Attach
✓ Query
✓ Tables
✓ Search
✓ Join
✓ Status
✓ Integrity
"""

import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path

from config import GEO_DB, HDP_DB
from database_bridge import (
    DatabaseBridge,
    DatabaseBridgeError,
)


# ==========================================================
# TEST CLASS
# ==========================================================

class TestDatabaseBridge(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.geo_db = GEO_DB
        cls.knowledge_db = HDP_DB

    def setUp(self):

        self.bridge = DatabaseBridge(
            geo_db=self.geo_db,
            knowledge_db=self.knowledge_db,
        )

    def tearDown(self):

        try:
            self.bridge.close()
        except Exception:
            pass

    # ==========================================================
    # CONNECTION TESTS
    # ==========================================================

    def test_connect(self):

        self.bridge.connect()

        self.assertTrue(self.bridge.connected)

        self.assertIsNotNone(self.bridge.conn)

    def test_database_list(self):

        self.bridge.connect()

        dbs = self.bridge.database_list()

        self.assertGreaterEqual(len(dbs), 2)

    def test_attached(self):

        self.bridge.connect()

        attached = self.bridge.attached()

        self.assertIn("main", attached)

        self.assertIn(self.bridge.alias, attached)

    def test_status(self):

        self.bridge.connect()

        status = self.bridge.status()

        self.assertTrue(status["connected"])

        self.assertTrue(status["geo_db"])

        self.assertTrue(status["knowledge_db"])

    def test_integrity(self):

        self.bridge.connect()

        result = self.bridge.integrity_check()

        self.assertEqual(result.lower(), "ok")

    # ==========================================================
    # TABLE TESTS
    # ==========================================================

    def test_main_tables(self):

        self.bridge.connect()

        tables = self.bridge.tables("main")

        self.assertIsInstance(tables, list)

        self.assertGreater(len(tables), 0)

    def test_knowledge_tables(self):

        self.bridge.connect()

        tables = self.bridge.tables("knowledge")

        self.assertIsInstance(tables, list)

        self.assertGreater(len(tables), 0)

    # ==========================================================
    # QUERY TESTS
    # ==========================================================

    def test_fetchone(self):

        self.bridge.connect()

        row = self.bridge.fetchone(
            "SELECT 1 AS value"
        )

        self.assertEqual(row["value"], 1)

    def test_fetchall(self):

        self.bridge.connect()

        rows = self.bridge.fetchall(
            """
            SELECT 1 AS id
            UNION ALL
            SELECT 2
            """
        )

        self.assertEqual(len(rows), 2)

    def test_fetchdict(self):

        self.bridge.connect()

        rows = self.bridge.fetchdict(
            """
            SELECT
                1 AS id,
                'HDP' AS name
            """
        )

        self.assertEqual(rows[0]["name"], "HDP")

    def test_fetchvalue(self):

        self.bridge.connect()

        value = self.bridge.fetchvalue(
            "SELECT 99"
        )

        self.assertEqual(value, 99)

    # ==========================================================
    # SEARCH TESTS
    # ==========================================================

    def test_table_exists(self):

        self.bridge.connect()

        tables = self.bridge.tables("main")

        self.assertGreater(len(tables), 0)

        self.assertTrue(
            self.bridge.table_exists(
                tables[0]
            )
        )

    def test_columns(self):

        self.bridge.connect()

        tables = self.bridge.tables("main")

        cols = self.bridge.columns(tables[0])

        self.assertIsInstance(cols, list)

    def test_count(self):

        self.bridge.connect()

        tables = self.bridge.tables("main")

        result = self.bridge.count(tables[0])

        self.assertIsInstance(result, int)

    # ==========================================================
    # STATUS TESTS
    # ==========================================================

    def test_repr(self):

        self.bridge.connect()

        text = repr(self.bridge)

        self.assertIn(
            "DatabaseBridge",
            text
        )

    def test_debug(self):

        self.bridge.connect()

        self.bridge.debug()

        self.assertTrue(True)

    # ==========================================================
    # JOIN TESTS
    # ==========================================================

    def test_join_query_method(self):

        self.bridge.connect()

        rows = self.bridge.join_query(
            "SELECT 1 AS id"
        )

        self.assertEqual(
            rows[0]["id"],
            1
        )

    def test_query_method(self):

        self.bridge.connect()

        rows = self.bridge.query(
            "SELECT 'bridge' AS name"
        )

        self.assertEqual(
            rows[0]["name"],
            "bridge"
        )

    # ==========================================================
    # FACTORY TESTS
    # ==========================================================

    def test_create_bridge(self):

        from database_bridge import create_bridge

        bridge = create_bridge(
            self.geo_db,
            self.knowledge_db
        )

        self.assertTrue(
            bridge.connected
        )

        bridge.close()

    # ==========================================================
    # ERROR TESTS
    # ==========================================================

    def test_invalid_geo_database(self):

        with self.assertRaises(
            DatabaseBridgeError
        ):

            bridge = DatabaseBridge(
                geo_db="/tmp/not_exists.db",
                knowledge_db=self.knowledge_db
            )

            bridge.connect()

    def test_invalid_hdp_database(self):

        with self.assertRaises(
            DatabaseBridgeError
        ):

            bridge = DatabaseBridge(
                geo_db=self.geo_db,
                knowledge_db="/tmp/not_exists.db"
            )

            bridge.connect()

    # ==========================================================
    # CONTEXT MANAGER
    # ==========================================================

    def test_context_manager(self):

        with DatabaseBridge(
            self.geo_db,
            self.knowledge_db
        ) as bridge:

            self.assertTrue(
                bridge.connected
            )

    # ==========================================================
    # SELF TEST
    # ==========================================================

    def test_health(self):

        self.bridge.connect()

        health = self.bridge.health()

        self.assertEqual(
            health["bridge"],
            "ok"
        )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print("HDP Bridge Test Suite")

    print("=" * 60)

    print()

    unittest.main(
        verbosity=2
    )
