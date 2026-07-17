#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bridge/v1/api.py

Public API

تمام پروژه فقط این فایل را import می‌کند.
"""

from database_bridge import DatabaseBridge
from bridge_service import BridgeService

from config import GEO_DB
from config import HDP_DB


__all__ = [

    "DatabaseBridge",

    "BridgeService",

    "create_bridge",

    "create_service",

]


# ==========================================================
# FACTORY
# ==========================================================

def create_bridge():

    bridge = DatabaseBridge(

        geo_db=GEO_DB,

        knowledge_db=HDP_DB,

    )

    bridge.connect()

    return bridge


def create_service():

    service = BridgeService(

        geo_db=GEO_DB,

        knowledge_db=HDP_DB,

    )

    return service


# ==========================================================
# VERSION
# ==========================================================

VERSION = "1.0.0"


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("HDP Bridge API")
    print("=" * 60)

    bridge = create_bridge()

    print(bridge.status())

    bridge.close()
