#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Bridge v1
============================================================

Read-only bridge between:

    • geo.db
    • hdp_v2.db

using SQLite ATTACH DATABASE.

No copy.
No migration.
No schema changes.

============================================================
"""

import re
import sqlite3

from pathlib import Path
from contextlib import contextmanager
from typing import Any, Dict, List

from config import GEO_DB
from config import HDP_DB


# ==========================================================
# VERSION
# ==========================================================

__version__ = "1.0.0"
__author__ = "HDP AI Core"
__license__ = "MIT"


# ==========================================================
# VALIDATION
# ==========================================================

_ALIAS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


# ==========================================================
# EXCEPTIONS
# ==========================================================

class DatabaseBridgeError(Exception):
    pass


# ==========================================================
# MAIN CLASS
# ==========================================================

class DatabaseBridge:

    def __init__(
        self,
        geo_db=GEO_DB,
        knowledge_db=HDP_DB,
        alias="knowledge",
    ):

        self.geo_db = Path(geo_db)
        self.knowledge_db = Path(knowledge_db)

        if not _ALIAS_RE.fullmatch(alias):
            raise DatabaseBridgeError(f"Invalid alias: {alias}")

        self.alias = alias

        self.conn = None
        self._connected = False

    # ======================================================

    def connect(self):

        if not self.geo_db.exists():
            raise DatabaseBridgeError(
                f"Geo database not found:\n{self.geo_db}"
            )

        if not self.knowledge_db.exists():
            raise DatabaseBridgeError(
                f"Knowledge database not found:\n{self.knowledge_db}"
            )

        uri = f"file:{self.geo_db}?mode=ro"

        self.conn = sqlite3.connect(
            uri,
            uri=True,
        )

        self.conn.row_factory = sqlite3.Row

        self.conn.execute(
            "PRAGMA foreign_keys=ON"
        )

        self.conn.execute(
            f"ATTACH DATABASE ? AS {self.alias}",
            (str(self.knowledge_db),),
        )

        self._connected = True

        return self.conn

    # ======================================================

    def close(self):

        if self.conn:

            try:
                self.conn.execute(
                    f"DETACH DATABASE {self.alias}"
                )
            except Exception:
                pass

            self.conn.close()

            self.conn = None
            self._connected = False

    # ======================================================

    def __enter__(self):

        self.connect()

        return self

    def __exit__(self, exc_type, exc, tb):

        self.close()

    # ======================================================

    @contextmanager
    def transaction(self):

        if self.conn is None:
            raise DatabaseBridgeError(
                "Bridge is not connected."
            )

        self.conn.execute("BEGIN")

        try:

            yield self

            self.conn.commit()

        except Exception:

            self.conn.rollback()

            raise

    # ======================================================
    # SQL
    # ======================================================

    def execute(self, sql, params=()):

        if self.conn is None:
            raise DatabaseBridgeError(
                "Bridge is not connected."
            )

        return self.conn.execute(sql, params)

    def fetchone(self, sql, params=()):

        return self.execute(sql, params).fetchone()

    def fetchall(self, sql, params=()):

        return self.execute(sql, params).fetchall()

    def fetchdict(self, sql, params=()):

        return [
            dict(row)
            for row in self.fetchall(sql, params)
        ]

    def fetchvalue(self, sql, params=()):

        row = self.fetchone(sql, params)

        if row is None:
            return None

        return row[0]

    # ======================================================
    # DATABASE
    # ======================================================

    def database_list(self):

        return self.fetchall(
            "PRAGMA database_list"
        )

    def attached(self):

        return [
            r[1]
            for r in self.database_list()
        ]

    def is_attached(self, alias):

        return alias in self.attached()

    def journal_mode(self):

        return self.fetchvalue(
            "PRAGMA journal_mode"
        )

    def integrity_check(self):

        return self.fetchvalue(
            "PRAGMA integrity_check"
        )

    # ======================================================
    # TABLES
    # ======================================================

    def tables(self, schema="main"):

        sql = f"""
        SELECT name
        FROM {schema}.sqlite_master
        WHERE type='table'
        ORDER BY name
        """

        return [
            r[0]
            for r in self.fetchall(sql)
        ]

    def table_exists(
        self,
        table,
        schema="main",
    ):

        sql = f"""
        SELECT name
        FROM {schema}.sqlite_master
        WHERE type='table'
        AND name=?
        """

        return self.fetchone(sql, (table,)) is not None

    def table_info(
        self,
        table,
        schema="main",
    ):

        return self.fetchdict(
            f"PRAGMA {schema}.table_info({table})"
        )

    def column_names(
        self,
        table,
        schema="main",
    ):

        return [
            r["name"]
            for r in self.table_info(table, schema)
        ]

    def columns(
        self,
        table,
        schema="main",
    ):
        """Alias for column_names()"""
        return self.column_names(table, schema)

    def count(
        self,
        table,
        schema="main",
    ):

        return self.fetchvalue(
            f"SELECT COUNT(*) FROM {schema}.{table}"
        )

    # ======================================================
    # SEARCH
    # ======================================================

    def search_like(
        self,
        table,
        column,
        keyword,
        schema="main",
    ):

        sql = f"""
        SELECT *
        FROM {schema}.{table}
        WHERE {column} LIKE ?
        """

        return self.fetchdict(
            sql,
            (f"%{keyword}%",),
        )

    def search_exact(
        self,
        table,
        column,
        value,
        schema="main",
    ):

        sql = f"""
        SELECT *
        FROM {schema}.{table}
        WHERE {column}=?
        """

        return self.fetchdict(sql, (value,))

    # ======================================================
    # JOIN
    # ======================================================

    def query(self, sql, params=()):

        return self.fetchdict(sql, params)

    def join_tables(
        self,
        left_table,
        right_table,
        left_column,
        right_column,
        columns="*",
        left_schema="main",
        right_schema="knowledge",
        where=None,
        params=(),
    ):

        sql = f"""
        SELECT {columns}

        FROM {left_schema}.{left_table} A

        INNER JOIN

        {right_schema}.{right_table} B

        ON

        A.{left_column}=B.{right_column}
        """

        if where:
            sql += f"\nWHERE {where}"

        return self.query(sql, params)

    # ======================================================
    # HDP
    # ======================================================

    def find_entity(
        self,
        entity,
        table="knowledge",
        column="title",
    ):

        sql = f"""
        SELECT *
        FROM knowledge.{table}
        WHERE {column} LIKE ?
        LIMIT 20
        """

        return self.query(
            sql,
            (f"%{entity}%",),
        )

    def find_relation(self, entity):

        sql = """
        SELECT *
        FROM knowledge.knowledge_relations
        WHERE source_entity LIKE ?
        OR target_entity LIKE ?
        """

        return self.query(
            sql,
            (
                f"%{entity}%",
                f"%{entity}%"
            ),
        )

    # ======================================================
    # GEO
    # ======================================================

    def find_place(
        self,
        keyword,
        table="places",
        column="name",
    ):

        sql = f"""
        SELECT *
        FROM main.{table}
        WHERE {column} LIKE ?
        LIMIT 50
        """

        return self.query(
            sql,
            (f"%{keyword}%",),
        )

    def search_everywhere(self, keyword):

        return {
            "knowledge": self.find_entity(keyword),
            "relations": self.find_relation(keyword),
            "places": self.find_place(keyword),
        }

    # ======================================================
    # STATUS
    # ======================================================

    def status(self):

        return {

            "connected": self._connected,

            "version": __version__,

            "geo_db": str(self.geo_db),

            "knowledge_db": str(self.knowledge_db),

            "attached": self.attached(),

            "journal_mode": self.journal_mode(),

            "integrity": self.integrity_check(),

        }

    # ======================================================

    def health(self):

        return {

            "bridge": "ok",

            "connected": self._connected,

            "geo_exists": self.geo_db.exists(),

            "knowledge_exists": self.knowledge_db.exists(),

            "attached": self.attached(),

            "journal_mode": self.journal_mode(),

            "integrity": self.integrity_check(),

        }

    # ======================================================

    def debug(self):

        print("=" * 60)
        print("Bridge Debug")
        print("=" * 60)

        for k, v in self.status().items():
            print(f"{k:<20} : {v}")

    # ======================================================

    @classmethod
    def open(
        cls,
        geo_db=GEO_DB,
        knowledge_db=HDP_DB,
    ):

        bridge = cls(
            geo_db=geo_db,
            knowledge_db=knowledge_db,
        )

        bridge.connect()

        return bridge

    # ======================================================

    @property
    def connected(self):
        """Return connection status"""
        return self._connected

    # ======================================================

    def __repr__(self):

        return (
            f"<DatabaseBridge "
            f"connected={self._connected} "
            f"geo={self.geo_db.name} "
            f"knowledge={self.knowledge_db.name}>"
        )


# ==========================================================
# FACTORY
# ==========================================================

def create_bridge(
    geo_db=GEO_DB,
    knowledge_db=HDP_DB,
):
    return DatabaseBridge.open(
        geo_db,
        knowledge_db,
    )


def open_bridge(
    geo_db=GEO_DB,
    knowledge_db=HDP_DB,
):
    return DatabaseBridge.open(
        geo_db,
        knowledge_db,
    )


def get_bridge(
    geo_db=GEO_DB,
    knowledge_db=HDP_DB,
):
    return DatabaseBridge.open(
        geo_db,
        knowledge_db,
    )


# ==========================================================
# SELF TEST
# ==========================================================

def self_test():

    with DatabaseBridge() as bridge:

        bridge.debug()

        print()

        print("MAIN TABLES")
        print(bridge.tables())

        print()

        print("KNOWLEDGE TABLES")
        print(bridge.tables("knowledge"))


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("HDP DATABASE BRIDGE v1")
    print("=" * 60)

    try:

        self_test()

        print("\nBridge OK")

    except Exception as e:

        print("\nBridge FAILED")
        print(e)
