"""
geo/database_bridge.py — read/query bridge between geo.db and HDP's
knowledge engine database (hdp_v2.db), via SQLite's native ATTACH DATABASE.

No data is copied or moved. Both files stay exactly as they are; this just
opens one sqlite3 connection that can see both schemas at once, so you can
JOIN a geo.db table against a knowledge-engine table in a single query
(e.g. "which POIs in geo.db are mentioned as entities in knowledge_relations").

IMPORTANT — read this before writing through the bridge:
SQLite's own documentation (https://sqlite.org/lang_attach.html) states
plainly: transactions across multiple ATTACHed databases are only atomic as
a set if the *main* database is not in WAL mode. geo.db's schema.sql sets
`PRAGMA journal_mode = WAL`, so a bridged connection inherits that -- each
individual database file stays internally consistent on a crash, but a
transaction that writes to both geo.db and the knowledge db in one COMMIT
is NOT guaranteed to land on both files together if the process dies mid-
commit (one file could persist the write, the other roll back).

Practical guidance:
  - Reads / cross-database JOINs: fully safe, no caveat applies.
  - Writes confined to one side (either geo.db OR the knowledge db, not
    both, per transaction): fully safe, same as using SpatialDB alone.
  - Writes that must touch both databases atomically: not safe over this
    bridge as-is. If that need ever comes up, either (a) restructure so
    each write only touches one file, or (b) accept eventual consistency
    (this is what most GraphRAG-style integrations do, since these are
    reference/index tables, not financial-transaction-grade data), or
    (c) drop WAL on whichever database is "main" for that specific write
    (real throughput cost, only worth it if true cross-db atomicity turns
    out to matter).

Usage:
    from geo.database_bridge import DatabaseBridge

    with DatabaseBridge("db/geo.db", "db/hdp_v2.db") as bridge:
        rows = bridge.query('''
            SELECT p.id, p.name, p.category, r.target_entity, r.weight
            FROM pois p
            JOIN knowledge.knowledge_relations r
              ON r.source_entity LIKE 'place:' || p.name || '%'
               OR r.source_entity LIKE 'city:' || p.name || '%'
        ''')
"""
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

_VALID_ALIAS = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class DatabaseBridgeError(Exception):
    pass


@dataclass
class DatabaseBridge:
    geo_db_path: str
    knowledge_db_path: str
    knowledge_alias: str = "knowledge"
    _conn: Optional[sqlite3.Connection] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        if not _VALID_ALIAS.match(self.knowledge_alias):
            raise DatabaseBridgeError(f"invalid schema alias: {self.knowledge_alias!r}")

    # ── lifecycle ────────────────────────────────────────────────────
    def connect(self) -> sqlite3.Connection:
        self._conn = sqlite3.connect(self.geo_db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        try:
            # Filename can be a bound parameter; the alias (schema name)
            # cannot -- it's validated above against an identifier pattern,
            # not user input, so the f-string here is not injectable.
            self._conn.execute(f"ATTACH DATABASE ? AS {self.knowledge_alias}", (self.knowledge_db_path,))
        except sqlite3.OperationalError as e:
            self._conn.close()
            self._conn = None
            raise DatabaseBridgeError(f"failed to attach {self.knowledge_db_path!r}: {e}") from e
        return self._conn

    def detach(self) -> None:
        if self._conn is not None:
            try:
                self._conn.execute(f"DETACH DATABASE {self.knowledge_alias}")
            except sqlite3.OperationalError:
                pass  # already detached / connection in a bad state -- close() will clean up

    def close(self) -> None:
        if self._conn is not None:
            self.detach()
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DatabaseBridge":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ── introspection (useful the first time you wire this up) ─────────
    def list_schemas(self) -> list:
        """PRAGMA database_list -- confirms both 'main' (geo.db) and the
        knowledge alias are attached and shows their file paths."""
        return [dict(r) for r in self._conn.execute("PRAGMA database_list").fetchall()]

    def tables_in(self, schema: str = "main") -> list:
        return [
            r[0] for r in self._conn.execute(
                f"SELECT name FROM {schema}.sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]

    # ── queries ──────────────────────────────────────────────────────
    def query(self, sql: str, params: tuple = ()) -> list:
        """Read-only convenience wrapper. Write statements work the same
        way via self._conn.execute(...) directly if needed, but see the
        atomicity warning in the module docstring first."""
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
