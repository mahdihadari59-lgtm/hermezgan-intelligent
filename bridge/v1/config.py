"""
bridge/v1/config.py

Database configuration.
"""

from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Geo Database
GEO_DB = PROJECT_ROOT / "geo.db"

# HDP Database candidates
HDP_DB_CANDIDATES = [

    Path.home() / "ai-system" / "hdp_x1" / "data" / "hdp_v2.db",

    Path.home() / "ai-system" / "hdp_x1" / "development" / "data" / "hdp_v2.db",

    Path.home() / "ai-system" / "hdp_x1" / "hdp_v2.db",

]

# First existing path
HDP_DB = next(
    (
        db
        for db in HDP_DB_CANDIDATES
        if db.exists()
    ),
    HDP_DB_CANDIDATES[0],
)

KNOWLEDGE_DB = HDP_DB

# SQLite Alias
GEO_ALIAS = "main"

KNOWLEDGE_ALIAS = "knowledge"

# SQLite timeout
SQLITE_TIMEOUT = 30
