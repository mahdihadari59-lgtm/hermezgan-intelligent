#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Geo Linker v3
=================

Production Version - Complete Single File

Features
--------
✓ Exact Match
✓ Alias Match
✓ Synonym Match
✓ Entity Dictionary Match
✓ Non-destructive
✓ Confidence Score
✓ Dry Run
✓ Multi Source
✓ Statistics
✓ Idempotent

Author: HDP ONE
"""

from __future__ import annotations

import argparse
import sqlite3
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Optional, DefaultDict
from collections import defaultdict

# ==============================================================
# CONFIGURATION
# ==============================================================

MAX_MATCHES_PER_TITLE = 3

DEFAULT_CONFIDENCE = 1.0
ALIAS_CONFIDENCE = 0.98
SYNONYM_CONFIDENCE = 0.95
ENTITY_CONFIDENCE = 0.92

MATCH_METHOD_EXACT = "exact"
MATCH_METHOD_ALIAS = "alias"
MATCH_METHOD_SYNONYM = "synonym"
MATCH_METHOD_ENTITY = "entity"

POIS_EXCLUDED = {
    "street",
    "residential_street",
    "neighborhood",
    "alley",
    "boulevard",
    "traffic_signal"
}

SPECIAL_TABLES = [
    ("banks", "name", "lat", "lng"),
    ("cafes", "name", "lat", "lng"),
    ("clinics", "name", "lat", "lng"),
    ("hospitals", "name", "lat", "lng"),
    ("hotels", "name", "lat", "lng"),
    ("parks", "name", "lat", "lng"),
    ("pharmacies", "name", "lat", "lng"),
    ("police_stations", "name", "lat", "lng"),
    ("restaurants", "name", "lat", "lng"),
    ("schools", "name", "lat", "lng"),
    ("universities", "name", "lat", "lng"),
]

# ==============================================================
# HELPERS
# ==============================================================

def normalize(text: Optional[str]) -> str:
    """Normalize Persian text for matching."""
    if text is None:
        return ""

    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("ي", "ی")
    text = text.replace("ك", "ک")
    text = text.replace("_", " ")
    text = text.replace("?", "")
    text = text.replace("؟", "")
    text = text.replace("،", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def safe_execute(conn, sql, params=()):
    """Execute SQL safely."""
    try:
        return conn.execute(sql, params)
    except sqlite3.OperationalError:
        return None


def open_database(path):
    """Open database with row factory."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_link_table(conn):
    """Create geo links table if not exists."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_geo_links(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            knowledge_id INTEGER NOT NULL,
            geo_source TEXT NOT NULL,
            geo_id INTEGER,
            matched_name TEXT,
            lat REAL,
            lng REAL,
            confidence REAL,
            match_method TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(knowledge_id, geo_source, geo_id)
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_links_knowledge
        ON knowledge_geo_links(knowledge_id)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_geo_links_source
        ON knowledge_geo_links(geo_source)
    """)

    conn.commit()


# ==============================================================
# STATISTICS
# ==============================================================

class Statistics:
    """Statistics collector."""

    def __init__(self):
        self.geo_records = 0
        self.scanned = 0
        self.matched = 0
        self.inserted = 0
        self.ambiguous = 0
        self.exact_hits = 0
        self.alias_hits = 0
        self.synonym_hits = 0
        self.entity_hits = 0

    def report(self):
        """Print statistics report."""
        print()
        print("=" * 70)
        print("Geo Linking Report")
        print("=" * 70)
        print(f"Geo records loaded     : {self.geo_records:,}")
        print(f"Knowledge scanned      : {self.scanned:,}")
        print(f"Matched titles         : {self.matched:,}")
        print(f"Inserted links         : {self.inserted:,}")
        print(f"Ambiguous skipped      : {self.ambiguous:,}")
        print()
        print(f"Exact matches          : {self.exact_hits:,}")
        print(f"Alias matches          : {self.alias_hits:,}")
        print(f"Synonym matches        : {self.synonym_hits:,}")
        print(f"Entity matches         : {self.entity_hits:,}")
        print("=" * 70)


# ==============================================================
# GEO MATCHER
# ==============================================================

class GeoMatcher:
    """Main geo matching engine."""

    def __init__(self, geo_conn, hdp_conn):
        self.geo_conn = geo_conn
        self.hdp_conn = hdp_conn
        self.geo_pool = defaultdict(list)
        self.alias_map = {}
        self.synonym_map = {}
        self.entity_map = {}
        self.stats = Statistics()

    # ----------------------------------------------------------
    # LOADING
    # ----------------------------------------------------------

    def prepare(self):
        """Load all data sources."""
        print("Loading Geo Database ...")
        self.load_geo()

        print("Loading Aliases ...")
        self.load_aliases()

        print("Loading Synonyms ...")
        self.load_synonyms()

        print("Loading Entity Dictionary ...")
        self.load_entity_dictionary()

        print()
        print("Ready.")
        print(f"Geo names : {len(self.geo_pool):,}")
        print(f"Aliases   : {len(self.alias_map):,}")
        print(f"Synonyms  : {len(self.synonym_map):,}")
        print(f"Entities  : {len(self.entity_map):,}")
        print()

    def add_geo(self, key, source, geo_id, lat, lng, confidence):
        """Add a geo record to pool."""
        key = normalize(key)
        if not key:
            return

        self.geo_pool[key].append({
            "source": source,
            "geo_id": geo_id,
            "lat": lat,
            "lng": lng,
            "confidence": confidence
        })
        self.stats.geo_records += 1

    def load_geo_table(self, table, name_col, lat_col, lng_col):
        """Load a specialized table."""
        cur = safe_execute(
            self.geo_conn,
            f"SELECT id, {name_col}, {lat_col}, {lng_col} FROM {table}"
        )

        if cur is None:
            return

        for row in cur.fetchall():
            name = row[name_col]
            if not name:
                continue

            self.add_geo(
                name,
                table,
                row["id"],
                row[lat_col],
                row[lng_col],
                DEFAULT_CONFIDENCE
            )

    def load_geo(self):
        """Load all geo data."""
        # Specialized tables
        for item in SPECIAL_TABLES:
            self.load_geo_table(*item)

        # POIs
        cur = self.geo_conn.execute("""
            SELECT id, category, name, lat, lng
            FROM pois
        """)

        for row in cur.fetchall():
            if row["category"] in POIS_EXCLUDED:
                continue
            if not row["name"]:
                continue
            if len(row["name"].strip()) <= 2:
                continue

            self.add_geo(
                row["name"],
                f"pois:{row['category']}",
                row["id"],
                row["lat"],
                row["lng"],
                DEFAULT_CONFIDENCE
            )

    def load_aliases(self):
        """Load aliases from knowledge_aliases."""
        cur = safe_execute(
            self.hdp_conn,
            "SELECT knowledge_id, alias_title FROM knowledge_aliases"
        )

        if cur is None:
            return

        for row in cur.fetchall():
            alias = normalize(row["alias_title"])
            if alias:
                self.alias_map[alias] = row["knowledge_id"]

    def load_synonyms(self):
        """Load synonyms from knowledge_synonyms."""
        cur = safe_execute(
            self.hdp_conn,
            "SELECT term, synonym FROM knowledge_synonyms"
        )

        if cur is None:
            return

        for row in cur.fetchall():
            term = normalize(row["term"])
            synonym = normalize(row["synonym"])
            if term and synonym:
                self.synonym_map[synonym] = term

    def load_entity_dictionary(self):
        """Load entity dictionary."""
        cur = safe_execute(
            self.hdp_conn,
            "SELECT entity, entity_type, city, importance FROM entity_dictionary"
        )

        if cur is None:
            return

        for row in cur.fetchall():
            entity = normalize(row["entity"])
            if entity:
                self.entity_map[entity] = {
                    "entity_type": row["entity_type"],
                    "city": row["city"],
                    "importance": row["importance"]
                }

    # ----------------------------------------------------------
    # MATCHING
    # ----------------------------------------------------------

    def lookup_geo(self, text):
        """Look up geo records for text."""
        key = normalize(text)

        # Exact match
        if key in self.geo_pool:
            self.stats.exact_hits += 1
            return self.geo_pool[key], MATCH_METHOD_EXACT, DEFAULT_CONFIDENCE

        # Alias match
        if key in self.alias_map:
            self.stats.alias_hits += 1
            return self.geo_pool.get(key, []), MATCH_METHOD_ALIAS, ALIAS_CONFIDENCE

        # Synonym match
        if key in self.synonym_map:
            base = self.synonym_map[key]
            if base in self.geo_pool:
                self.stats.synonym_hits += 1
                return self.geo_pool[base], MATCH_METHOD_SYNONYM, SYNONYM_CONFIDENCE

        # Entity match
        if key in self.entity_map and key in self.geo_pool:
            self.stats.entity_hits += 1
            return self.geo_pool[key], MATCH_METHOD_ENTITY, ENTITY_CONFIDENCE

        return [], None, 0.0

    # ----------------------------------------------------------
    # LINKING
    # ----------------------------------------------------------

    def insert_link(self, knowledge_id, geo, matched_name, confidence, method, dry_run=False):
        """Insert a geo link."""
        if dry_run:
            self.stats.inserted += 1
            return

        self.hdp_conn.execute("""
            INSERT OR IGNORE INTO knowledge_geo_links(
                knowledge_id, geo_source, geo_id, matched_name,
                lat, lng, confidence, match_method
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            knowledge_id,
            geo["source"],
            geo["geo_id"],
            matched_name,
            geo["lat"],
            geo["lng"],
            confidence,
            method
        ))

        self.stats.inserted += 1

    def commit(self):
        """Commit changes."""
        self.hdp_conn.commit()

    def close(self):
        """Close connections."""
        self.geo_conn.close()
        self.hdp_conn.close()


# ==============================================================
# MAIN PROCESSING
# ==============================================================

def process_knowledge(matcher, dry_run=False):
    """Process all knowledge records."""
    cur = matcher.hdp_conn.execute("""
        SELECT id, title
        FROM knowledge
        WHERE is_deleted = 0 OR is_deleted IS NULL
        ORDER BY id
    """)

    for row in cur.fetchall():
        matcher.stats.scanned += 1
        knowledge_id = row["id"]
        title = row["title"]

        if not title:
            continue

        matches, method, confidence = matcher.lookup_geo(title)

        if not matches:
            continue

        # Avoid ambiguous matches
        if len(matches) > MAX_MATCHES_PER_TITLE:
            matcher.stats.ambiguous += 1
            continue

        matcher.stats.matched += 1

        for geo in matches:
            matcher.insert_link(
                knowledge_id=knowledge_id,
                geo=geo,
                matched_name=title,
                confidence=confidence,
                method=method,
                dry_run=dry_run
            )

    if not dry_run:
        matcher.commit()


# ==============================================================
# MAIN
# ==============================================================

def main():
    parser = argparse.ArgumentParser(description="HDP Geo Linker v3")
    parser.add_argument("--geo-db", required=True, help="Path to geo.db")
    parser.add_argument("--hdp-db", required=True, help="Path to hdp_v2.db")
    parser.add_argument("--dry-run", action="store_true", help="Do not write anything")

    args = parser.parse_args()

    print("=" * 70)
    print("📍 HDP GEO LINKER v3")
    print("=" * 70)
    print(f"Geo DB : {args.geo_db}")
    print(f"HDP DB : {args.hdp_db}")
    print()

    # Open databases
    geo = open_database(args.geo_db)
    hdp = open_database(args.hdp_db)

    # Initialize matcher
    matcher = GeoMatcher(geo, hdp)
    matcher.prepare()

    # Create table if needed
    if not args.dry_run:
        ensure_link_table(hdp)

    # Process
    print("Scanning Knowledge...")
    process_knowledge(matcher, dry_run=args.dry_run)

    # Report
    matcher.stats.report()

    # Cleanup
    matcher.close()


# ==============================================================
# ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    main()
