#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backend" / "data" / "hdp_v2.db"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = SOURCE.with_name(f"hdp_v2_pre_repair_{STAMP}.db")
OUTPUT = SOURCE.with_name("hdp_v2_repaired.db")


def die(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(1)


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type='table' AND name=?
        """,
        (name,),
    ).fetchone()
    return row is not None


def scalar(conn: sqlite3.Connection, sql: str) -> int:
    row = conn.execute(sql).fetchone()
    return int(row[0] or 0)


def main() -> None:
    if not SOURCE.exists():
        die(f"Database not found: {SOURCE}")

    print(f"[1/9] Source: {SOURCE}")
    print(f"[2/9] Backup: {BACKUP}")
    print(f"[3/9] Output: {OUTPUT}")

    # ------------------------------------------------------------------
    # 1. Physical backup of original
    # ------------------------------------------------------------------
    shutil.copy2(SOURCE, BACKUP)

    # Remove previous generated output only.
    if OUTPUT.exists():
        OUTPUT.unlink()

    src = sqlite3.connect(str(SOURCE))
    src.row_factory = sqlite3.Row

    # Basic source checks.
    integrity = src.execute("PRAGMA integrity_check;").fetchone()[0]
    if integrity != "ok":
        src.close()
        die(f"Source integrity_check failed: {integrity}")

    required = ["knowledge", "graph_nodes", "graph_edges"]
    for name in required:
        if not table_exists(src, name):
            src.close()
            die(f"Required table missing: {name}")

    knowledge_count = scalar(src, "SELECT COUNT(*) FROM knowledge")
    node_count = scalar(src, "SELECT COUNT(*) FROM graph_nodes")
    edge_count = scalar(src, "SELECT COUNT(*) FROM graph_edges")

    print(f"    knowledge      = {knowledge_count}")
    print(f"    graph_nodes    = {node_count}")
    print(f"    graph_edges    = {edge_count}")

    # ------------------------------------------------------------------
    # 2. Copy entire DB to repaired DB
    # ------------------------------------------------------------------
    dst = sqlite3.connect(str(OUTPUT))
    src.backup(dst)
    dst.commit()
    src.close()

    dst.execute("PRAGMA foreign_keys = ON;")
    dst.execute("PRAGMA synchronous = NORMAL;")
    dst.execute("PRAGMA journal_mode = WAL;")

    # ------------------------------------------------------------------
    # 3. Repair run / audit tables
    # ------------------------------------------------------------------
    dst.executescript(
        """
        CREATE TABLE IF NOT EXISTS repair_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            source_db TEXT NOT NULL,
            output_db TEXT NOT NULL,
            status TEXT NOT NULL,
            knowledge_count INTEGER,
            graph_nodes_count INTEGER,
            graph_edges_before INTEGER,
            graph_edges_after INTEGER,
            orphan_count INTEGER,
            duplicate_count INTEGER,
            self_loop_count INTEGER
        );

        CREATE TABLE IF NOT EXISTS graph_edges_legacy_quarantine (
            quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_edge_id INTEGER NOT NULL,
            source_id INTEGER,
            target_id INTEGER,
            relation_type TEXT,
            weight REAL,
            confidence REAL,
            created_at DATETIME,
            reason TEXT NOT NULL,
            quarantined_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS graph_edges_duplicate_quarantine (
            quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_edge_id INTEGER NOT NULL,
            source_id INTEGER,
            target_id INTEGER,
            relation_type TEXT,
            weight REAL,
            confidence REAL,
            created_at DATETIME,
            kept_edge_id INTEGER,
            reason TEXT NOT NULL,
            quarantined_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            object_type TEXT,
            object_id INTEGER,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    started_at = datetime.now().isoformat(timespec="seconds")

    # ------------------------------------------------------------------
    # 4. Canonical architectural tables
    # ------------------------------------------------------------------
    dst.executescript(
        """
        CREATE TABLE IF NOT EXISTS graph_entities (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            properties TEXT,
            confidence REAL NOT NULL DEFAULT 1.0
                CHECK(confidence >= 0 AND confidence <= 1)
        );

        CREATE TABLE IF NOT EXISTS graph_entity_alias (
            entity_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            UNIQUE(entity_id, alias),
            FOREIGN KEY(entity_id) REFERENCES graph_entities(id)
        );

        CREATE TABLE IF NOT EXISTS ontology_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS knowledge_meta (
            knowledge_id INTEGER PRIMARY KEY,
            category TEXT,
            subcategory TEXT,
            source TEXT,
            topic TEXT,
            main_intent TEXT,
            sub_intent TEXT,
            expert_name TEXT,
            status TEXT,
            verified INTEGER,
            confidence REAL,
            FOREIGN KEY(knowledge_id) REFERENCES knowledge(id)
        );

        CREATE TABLE IF NOT EXISTS reasoning_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL UNIQUE,
            condition TEXT NOT NULL,
            conclusion TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            enabled INTEGER DEFAULT 1
        );
        """
    )

    # ------------------------------------------------------------------
    # 5. Build graph_entities from the proven node/knowledge mapping.
    # graph_nodes.id == knowledge.id == graph_nodes.knowledge_id
    # ------------------------------------------------------------------
    dst.execute("DELETE FROM graph_entities;")

    dst.execute(
        """
        INSERT INTO graph_entities (
            id,
            title,
            entity_type,
            properties,
            confidence
        )
        SELECT
            n.id,
            COALESCE(k.title, n.title, ''),
            COALESCE(NULLIF(n.node_type, ''), 'Knowledge'),
            json_object(
                'knowledge_id', n.knowledge_id,
                'parent_id', n.parent_id,
                'root_id', n.root_id,
                'depth', n.depth,
                'level', n.level,
                'path', n.path,
                'children_count', n.children_count,
                'is_leaf', n.is_leaf
            ),
            CASE
                WHEN n.score IS NULL THEN 1.0
                WHEN n.score < 0 THEN 0.0
                WHEN n.score > 1 THEN 1.0
                ELSE n.score
            END
        FROM graph_nodes n
        LEFT JOIN knowledge k
            ON k.id = n.knowledge_id
        WHERE n.knowledge_id IS NOT NULL
          AND k.id IS NOT NULL;
        """
    )

    # Ontology classes directly from current graph node types.
    dst.execute("DELETE FROM ontology_classes;")
    dst.execute(
        """
        INSERT OR IGNORE INTO ontology_classes(name)
        SELECT DISTINCT entity_type
        FROM graph_entities
        WHERE entity_type IS NOT NULL
          AND TRIM(entity_type) <> '';
        """
    )

    # Knowledge metadata.
    dst.execute("DELETE FROM knowledge_meta;")
    dst.execute(
        """
        INSERT INTO knowledge_meta (
            knowledge_id,
            category,
            subcategory,
            source,
            topic,
            main_intent,
            sub_intent,
            expert_name,
            status,
            verified,
            confidence
        )
        SELECT
            id,
            category,
            subcategory,
            source,
            topic,
            main_intent,
            sub_intent,
            expert_name,
            status,
            verified,
            confidence
        FROM knowledge;
        """
    )

    # ------------------------------------------------------------------
    # 6. Rebuild graph_edges safely.
    #
    # Rules:
    #   - both endpoints must exist
    #   - no self-loop
    #   - logical duplicate kept once
    #   - orphan edges preserved in quarantine
    # ------------------------------------------------------------------
    now = datetime.now().isoformat(timespec="seconds")

    orphan_before = scalar(
        dst,
        """
        SELECT COUNT(*)
        FROM graph_edges e
        LEFT JOIN graph_nodes s ON s.id=e.source_id
        LEFT JOIN graph_nodes t ON t.id=e.target_id
        WHERE s.id IS NULL OR t.id IS NULL
        """,
    )

    self_loops = scalar(
        dst,
        """
        SELECT COUNT(*)
        FROM graph_edges
        WHERE source_id = target_id
        """,
    )

    duplicate_count = scalar(
        dst,
        """
        SELECT COUNT(*)
        FROM (
            SELECT source_id, target_id, relation_type
            FROM graph_edges
            GROUP BY source_id, target_id, relation_type
            HAVING COUNT(*) > 1
        )
        """,
    )

    # Quarantine orphans.
    dst.execute(
        """
        INSERT INTO graph_edges_legacy_quarantine (
            original_edge_id,
            source_id,
            target_id,
            relation_type,
            weight,
            confidence,
            created_at,
            reason,
            quarantined_at
        )
        SELECT
            e.id,
            e.source_id,
            e.target_id,
            e.relation_type,
            e.weight,
            e.confidence,
            e.created_at,
            CASE
                WHEN s.id IS NULL AND t.id IS NULL THEN 'both_endpoints_missing'
                WHEN s.id IS NULL THEN 'source_endpoint_missing'
                WHEN t.id IS NULL THEN 'target_endpoint_missing'
                ELSE 'unknown'
            END,
            ?
        FROM graph_edges e
        LEFT JOIN graph_nodes s ON s.id=e.source_id
        LEFT JOIN graph_nodes t ON t.id=e.target_id
        WHERE s.id IS NULL OR t.id IS NULL
        """,
        (now,),
    )

    # Quarantine self loops.
    dst.execute(
        """
        INSERT INTO graph_edges_legacy_quarantine (
            original_edge_id,
            source_id,
            target_id,
            relation_type,
            weight,
            confidence,
            created_at,
            reason,
            quarantined_at
        )
        SELECT
            e.id,
            e.source_id,
            e.target_id,
            e.relation_type,
            weight,
            confidence,
            created_at,
            'self_loop',
            ?
        FROM graph_edges
        WHERE source_id = target_id
        """,
        (now,),
    )

    # Create clean edge table, same API-facing columns, with real FKs.
    dst.executescript(
        """
        DROP TABLE IF EXISTS graph_edges_clean;

        CREATE TABLE graph_edges_clean (
            id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            confidence REAL NOT NULL DEFAULT 1.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            CHECK(source_id <> target_id),
            CHECK(confidence >= 0 AND confidence <= 1),
            FOREIGN KEY(source_id) REFERENCES graph_nodes(id),
            FOREIGN KEY(target_id) REFERENCES graph_nodes(id),
            UNIQUE(source_id, target_id, relation_type)
        );
        """
    )

    # Keep the best edge per logical relationship.
    dst.execute(
        """
        INSERT INTO graph_edges_clean (
            id,
            source_id,
            target_id,
            relation_type,
            weight,
            confidence,
            created_at
        )
        SELECT
            e.id,
            e.source_id,
            e.target_id,
            e.relation_type,
            COALESCE(e.weight, 1.0),
            CASE
                WHEN e.confidence IS NULL THEN 1.0
                WHEN e.confidence < 0 THEN 0.0
                WHEN e.confidence > 1 THEN 1.0
                ELSE e.confidence
            END,
            e.created_at
        FROM (
            SELECT
                e.*,
                ROW_NUMBER() OVER (
                    PARTITION BY e.source_id, e.target_id, e.relation_type
                    ORDER BY
                        CASE WHEN e.confidence IS NULL THEN 0 ELSE e.confidence END DESC,
                        CASE WHEN e.weight IS NULL THEN 0 ELSE e.weight END DESC,
                        e.id DESC
                ) AS rn
            FROM graph_edges e
            JOIN graph_nodes s ON s.id=e.source_id
            JOIN graph_nodes t ON t.id=e.target_id
            WHERE e.source_id <> e.target_id
        ) AS e
        WHERE e.rn = 1;
        """
    )

    # Quarantine duplicate logical edges not chosen.
    dst.execute(
        """
        INSERT INTO graph_edges_duplicate_quarantine (
            original_edge_id,
            source_id,
            target_id,
            relation_type,
            weight,
            confidence,
            created_at,
            kept_edge_id,
            reason,
            quarantined_at
        )
        SELECT
            e.id,
            e.source_id,
            e.target_id,
            e.relation_type,
            e.weight,
            e.confidence,
            e.created_at,
            c.id,
            'duplicate_logical_edge',
            ?
        FROM graph_edges e
        JOIN graph_nodes s ON s.id=e.source_id
        JOIN graph_nodes t ON t.id=e.target_id
        JOIN graph_edges_clean c
          ON c.source_id=e.source_id
         AND c.target_id=e.target_id
         AND c.relation_type=e.relation_type
        WHERE e.id <> c.id
          AND e.source_id <> e.target_id
        """,
        (now,),
    )

    # Preserve original table under a versioned historical name.
    dst.execute("DROP TABLE IF EXISTS graph_edges_original;")
    dst.execute("ALTER TABLE graph_edges RENAME TO graph_edges_original;")
    dst.execute("ALTER TABLE graph_edges_clean RENAME TO graph_edges;")

    # Useful indexes.
    dst.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_graph_edges_source
            ON graph_edges(source_id);

        CREATE INDEX IF NOT EXISTS idx_graph_edges_target
            ON graph_edges(target_id);

        CREATE INDEX IF NOT EXISTS idx_graph_edges_relation
            ON graph_edges(relation_type);

        CREATE INDEX IF NOT EXISTS idx_graph_entities_type
            ON graph_entities(entity_type);

        CREATE INDEX IF NOT EXISTS idx_graph_entities_title
            ON graph_entities(title);

        CREATE INDEX IF NOT EXISTS idx_knowledge_meta_category
            ON knowledge_meta(category);
        """
    )

    # ------------------------------------------------------------------
    # 7. Final validation
    # ------------------------------------------------------------------
    valid_edges = scalar(dst, "SELECT COUNT(*) FROM graph_edges")

    remaining_orphans = scalar(
        dst,
        """
        SELECT COUNT(*)
        FROM graph_edges e
        LEFT JOIN graph_nodes s ON s.id=e.source_id
        LEFT JOIN graph_nodes t ON t.id=e.target_id
        WHERE s.id IS NULL OR t.id IS NULL
        """,
    )

    remaining_self_loops = scalar(
        dst,
        """
        SELECT COUNT(*)
        FROM graph_edges
        WHERE source_id = target_id
        """,
    )

    fk_errors = dst.execute("PRAGMA foreign_key_check;").fetchall()
    final_integrity = dst.execute("PRAGMA integrity_check;").fetchone()[0]

    if remaining_orphans != 0:
        dst.rollback()
        dst.close()
        die(f"Repair failed: {remaining_orphans} orphan edges remain")

    if remaining_self_loops != 0:
        dst.rollback()
        dst.close()
        die(f"Repair failed: {remaining_self_loops} self-loops remain")

    if fk_errors:
        dst.rollback()
        dst.close()
        die(f"Repair failed: foreign_key_check returned {len(fk_errors)} rows")

    if final_integrity != "ok":
        dst.rollback()
        dst.close()
        die(f"Repair failed: integrity_check = {final_integrity}")

    # ------------------------------------------------------------------
    # 8. Record repair result
    # ------------------------------------------------------------------
    dst.execute(
        """
        INSERT INTO repair_runs (
            started_at,
            source_db,
            output_db,
            status,
            knowledge_count,
            graph_nodes_count,
            graph_edges_before,
            graph_edges_after,
            orphan_count,
            duplicate_count,
            self_loop_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            started_at,
            str(SOURCE),
            str(OUTPUT),
            "SUCCESS",
            knowledge_count,
            node_count,
            edge_count,
            valid_edges,
            orphan_before,
            duplicate_count,
            self_loops,
        ),
    )

    dst.execute(
        """
        INSERT INTO audit_log(event_type, object_type, object_id, message)
        VALUES (?, ?, ?, ?)
        """,
        (
            "DATA1_REPAIR",
            "database",
            None,
            json.dumps(
                {
                    "source": str(SOURCE),
                    "output": str(OUTPUT),
                    "backup": str(BACKUP),
                    "knowledge": knowledge_count,
                    "graph_nodes": node_count,
                    "graph_edges_before": edge_count,
                    "graph_edges_after": valid_edges,
                    "orphans_quarantined": orphan_before,
                    "duplicates_quarantined": duplicate_count,
                    "self_loops_quarantined": self_loops,
                },
                ensure_ascii=False,
            ),
        ),
    )

    dst.commit()

    print()
    print("========================================")
    print("DATA 1 REPAIR SUCCESS")
    print("========================================")
    print(f"Original      : {SOURCE}")
    print(f"Backup        : {BACKUP}")
    print(f"Repaired DB   : {OUTPUT}")
    print(f"Knowledge     : {knowledge_count}")
    print(f"Graph nodes   : {node_count}")
    print(f"Edges before  : {edge_count}")
    print(f"Edges active  : {valid_edges}")
    print(f"Orphans       : {orphan_before} -> quarantined")
    print(f"Duplicates    : {duplicate_count} -> quarantined")
    print(f"Self loops    : {self_loops} -> quarantined")
    print("Foreign keys  : OK")
    print("Integrity     : OK")
    print("========================================")

    dst.close()


if __name__ == "__main__":
    main()
