#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Bridge Service v1

Service Layer

geo.db
        ↓
DatabaseBridge
        ↓
HDP Services

تمام ماژول‌های پروژه فقط از این فایل استفاده می‌کنند.
"""

from pathlib import Path

from config import GEO_DB
from config import HDP_DB

from database_bridge import DatabaseBridge


class BridgeService:

    def __init__(
        self,
        geo_db=GEO_DB,
        knowledge_db=HDP_DB,
    ):

        self.bridge = DatabaseBridge(
            geo_db=geo_db,
            knowledge_db=knowledge_db,
        )

        self.connected = False

    # ======================================================
    # CONNECTION
    # ======================================================

    def connect(self):

        if self.connected:
            return

        self.bridge.connect()

        self.connected = True

    def disconnect(self):

        if not self.connected:
            return

        self.bridge.close()

        self.connected = False

    def __enter__(self):

        self.connect()

        return self

    def __exit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        self.disconnect()

    # ======================================================
    # KNOWLEDGE API
    # ======================================================

    def find_entity(
        self,
        name,
    ):
        """
        Search entity inside HDP knowledge database.
        """

        self.connect()

        return self.bridge.find_entity(name)

    def find_relation(
        self,
        entity,
    ):
        """
        Search relations.
        """

        self.connect()

        return self.bridge.find_relation(entity)

    # ======================================================
    # GEO API
    # ======================================================

    def find_place(
        self,
        keyword,
    ):
        """
        Search places inside geo.db
        """

        self.connect()

        return self.bridge.find_place(keyword)

    def search(
        self,
        keyword,
    ):
        """
        Search everywhere.
        """

        self.connect()

        return self.bridge.search_everywhere(keyword)

    # ======================================================
    # DATABASE STATUS
    # ======================================================

    def status(self):

        self.connect()

        return self.bridge.status()

    # ======================================================
    # JOIN API
    # ======================================================

    def hospital_knowledge(self):
        """
        Join hospitals with knowledge graph.
        """

        self.connect()

        return self.bridge.hospital_knowledge()

    def place_knowledge(
        self,
        table,
        column="name",
    ):
        """
        Generic JOIN helper.
        """

        self.connect()

        return self.bridge.place_knowledge(
            table=table,
            column=column,
        )

    def custom_join(
        self,
        left_table,
        right_table,
        left_column,
        right_column,
        columns="*",
        where=None,
        params=(),
    ):
        """
        Generic SQL JOIN.
        """

        self.connect()

        return self.bridge.join_tables(
            left_table=left_table,
            right_table=right_table,
            left_column=left_column,
            right_column=right_column,
            columns=columns,
            where=where,
            params=params,
        )

    # ======================================================
    # HEALTH
    # ======================================================

    def health(self):
        """
        Service health.
        """

        self.connect()

        return self.bridge.health()

    def debug(self):
        """
        Print debug information.
        """

        self.connect()

        self.bridge.debug()


# ==========================================================
# SINGLETON
# ==========================================================

_service = None


def get_service():
    """
    Global BridgeService instance.
    """

    global _service

    if _service is None:
        _service = BridgeService()

    return _service


def create_service():
    """
    Create new BridgeService.
    """

    return BridgeService()


# ==========================================================
# VERSION
# ==========================================================

__version__ = "1.0.0"
__author__ = "HDP AI Core"


# ==========================================================
# MAIN
# ==========================================================

def main():

    service = BridgeService()

    with service:

        print("=" * 60)
        print("HDP BRIDGE SERVICE")
        print("=" * 60)

        print()

        print(service.status())

        print()

        print(service.health())

        print()

        print("Search Example")

        result = service.search("بندرعباس")

        for key, value in result.items():

            print(f"{key}: {len(value)} rows")


if __name__ == "__main__":
    main()
