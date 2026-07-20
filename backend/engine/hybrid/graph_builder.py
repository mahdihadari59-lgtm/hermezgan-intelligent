#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/graph_builder.py
-------------------------------------------------------
مسئول ساخت و نگهداری گراف دانش HDP.

اصول معماری‌ای که در این فایل رعایت شده (طبق تصمیمات قبلی پروژه):
    1) Dedup بر اساس عنوان نرمال‌شده (title-based)، نه ID.
    2) نوع رابطه بین دو نود (relation_type) از جدول قابل‌تنظیم
       `relation_rules` خوانده می‌شود، نه با if/else هارد-کد.
    3) Schema گراف در سه جدول مجزا: graph_nodes, graph_edges,
       graph_properties.
    4) نرمال‌سازی متن فارسی (NFKD، حذف نیم‌فاصله، یکسان‌سازی
       ي/ی و ك/ک) پیش از هر مقایسه‌ای انجام می‌شود.

فقط کتابخانه استاندارد پایتون؛ بدون وابستگی خارجی.
-------------------------------------------------------
"""

import sqlite3
import re
import unicodedata
import time
from typing import Optional, List, Dict, Any, Tuple

from engine.hybrid.config import HybridConfig


# =========================================================
# نرمال‌سازی متن فارسی
# (این تابع باید با نسخه‌های موجود در knowledge-search.py و
#  hybrid-intent-engine.js هم‌راستا بماند. در آینده باید به
#  engine/hybrid/utils.py منتقل شود تا یک نسخه واحد باشد.)
# =========================================================
_FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_AR_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_DIACRITICS_RE = re.compile(r"[\u064B-\u065F\u0670]")
_NON_TEXT_RE = re.compile(r"[^\u0600-\u06FF\u0750-\u077Fa-zA-Z0-9\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_persian(text: Optional[str]) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKD", text)
    t = t.replace("\u200c", " ")
    t = t.replace("ي", "ی").replace("ى", "ی")
    t = t.replace("ك", "ک")
    t = t.replace("ۀ", "ه").replace("ة", "ه")
    for ch in "إأآا":
        t = t.replace(ch, "ا")
    t = t.replace("ؤ", "و").replace("ئ", "ی")
    t = _DIACRITICS_RE.sub("", t)
    for i, d in enumerate(_FA_DIGITS):
        t = t.replace(d, str(i))
    for i, d in enumerate(_AR_DIGITS):
        t = t.replace(d, str(i))
    t = _NON_TEXT_RE.sub(" ", t)
    t = _MULTI_SPACE_RE.sub(" ", t).strip()
    return t.lower()


class GraphBuilder:
    """
    رابط اصلی ساخت/به‌روزرسانی گراف دانش.
    تمام عملیات نوشتن (write) روی SQLite از این کلاس عبور می‌کند
    تا قوانین dedup و relation_rules یکجا و سازگار رعایت شوند.
    """

    DEFAULT_RELATION_RULES: List[Dict[str, Any]] = [
        # قوانین پیش‌فرض فقط برای seed اولیه‌اند؛ در عمل جدول
        # relation_rules باید از پنل/دیتابیس قابل ویرایش باشد.
        {"source_type": "*", "target_type": "*", "relation_type": "related_to", "weight": 1.0},
        {"source_type": "incident", "target_type": "status", "relation_type": "causes", "weight": 1.2},
        {"source_type": "service", "target_type": "facility", "relation_type": "near", "weight": 0.8},
        {"source_type": "attraction", "target_type": "attraction", "relation_type": "nearby", "weight": 0.9},
    ]

    def __init__(self, db_path: Optional[str] = None, seed_default_rules: bool = True):
        self.db_path = db_path or HybridConfig.DB_PATH
        HybridConfig.ensure_data_dir()
        self._ensure_schema()
        if seed_default_rules:
            self._seed_relation_rules_if_empty()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # -----------------------------------------------------
    # Schema
    # -----------------------------------------------------
    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    title_normalized TEXT NOT NULL,
                    content TEXT,
                    node_type TEXT,
                    domain TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_title_normalized "
                "ON graph_nodes(title_normalized)"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at TEXT,
                    FOREIGN KEY(source_id) REFERENCES graph_nodes(id),
                    FOREIGN KEY(target_id) REFERENCES graph_nodes(id)
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source_id)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target_id)"
            )
            # جلوگیری از یال تکراری بین دو نود با همان relation_type
            cur.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_edges_unique "
                "ON graph_edges(source_id, target_id, relation_type)"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS graph_properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY(node_id) REFERENCES graph_nodes(id)
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_properties_node ON graph_properties(node_id)"
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS relation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def _seed_relation_rules_if_empty(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM relation_rules")
            count = cur.fetchone()[0]
            if count == 0:
                for rule in self.DEFAULT_RELATION_RULES:
                    cur.execute(
                        "INSERT INTO relation_rules (source_type, target_type, relation_type, weight) "
                        "VALUES (?, ?, ?, ?)",
                        (rule["source_type"], rule["target_type"], rule["relation_type"], rule["weight"]),
                    )
                conn.commit()
        finally:
            conn.close()

    # -----------------------------------------------------
    # Nodeها (با dedup بر اساس عنوان نرمال‌شده)
    # -----------------------------------------------------
    def find_node_by_title(self, title: str) -> Optional[sqlite3.Row]:
        normalized = normalize_persian(title)
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM graph_nodes WHERE title_normalized = ?", (normalized,)
            )
            return cur.fetchone()
        finally:
            conn.close()

    def add_node(
        self,
        title: str,
        content: str = "",
        node_type: str = "generic",
        domain: str = "",
        merge_content: bool = True,
    ) -> int:
        """
        اگر نودی با همین عنوان نرمال‌شده وجود داشته باشد، به‌جای
        ساخت نود جدید، آن را به‌روزرسانی می‌کند (dedup واقعی، نه
        فقط جلوگیری از خطا).
        @returns: id نود (چه جدید چه موجود)
        """
        normalized = normalize_persian(title)
        now = self._now()

        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, content FROM graph_nodes WHERE title_normalized = ?",
                (normalized,),
            )
            existing = cur.fetchone()

            if existing:
                node_id = existing["id"]
                if merge_content and content and content not in (existing["content"] or ""):
                    new_content = f"{existing['content'] or ''}\n{content}".strip()
                    cur.execute(
                        "UPDATE graph_nodes SET content = ?, updated_at = ? WHERE id = ?",
                        (new_content, now, node_id),
                    )
                    conn.commit()
                return node_id

            cur.execute(
                "INSERT INTO graph_nodes "
                "(title, title_normalized, content, node_type, domain, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, normalized, content, node_type, domain, now, now),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def add_property(self, node_id: int, key: str, value: str) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO graph_properties (node_id, key, value) VALUES (?, ?, ?)",
                (node_id, key, value),
            )
            conn.commit()
        finally:
            conn.close()

    def get_properties(self, node_id: int) -> Dict[str, str]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM graph_properties WHERE node_id = ?", (node_id,))
            return {row["key"]: row["value"] for row in cur.fetchall()}
        finally:
            conn.close()

    # -----------------------------------------------------
    # Edgeها (relation_type از relation_rules خوانده می‌شود)
    # -----------------------------------------------------
    def resolve_relation(self, source_type: str, target_type: str) -> Tuple[str, float]:
        """
        قانون رابطه بین دو نوع نود را از جدول relation_rules می‌خواند.
        اولویت: تطابق دقیق source_type+target_type
               > تطابق با wildcard (*)
               > پیش‌فرض نهایی related_to/1.0
        """
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT relation_type, weight FROM relation_rules "
                "WHERE source_type = ? AND target_type = ? LIMIT 1",
                (source_type, target_type),
            )
            row = cur.fetchone()
            if row:
                return row["relation_type"], row["weight"]

            cur.execute(
                "SELECT relation_type, weight FROM relation_rules "
                "WHERE source_type = '*' AND target_type = '*' LIMIT 1"
            )
            row = cur.fetchone()
            if row:
                return row["relation_type"], row["weight"]

            return "related_to", 1.0
        finally:
            conn.close()

    def add_edge(
        self,
        source_id: int,
        target_id: int,
        relation_type: Optional[str] = None,
        weight: Optional[float] = None,
    ) -> int:
        """
        اگر relation_type/weight داده نشود، از resolve_relation بر اساس
        node_type دو طرف به‌صورت خودکار محاسبه می‌شود.
        """
        if relation_type is None or weight is None:
            source_type, target_type = self._node_types(source_id, target_id)
            resolved_type, resolved_weight = self.resolve_relation(source_type, target_type)
            relation_type = relation_type or resolved_type
            weight = weight if weight is not None else resolved_weight

        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO graph_edges "
                "(source_id, target_id, relation_type, weight, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (source_id, target_id, relation_type, weight, self._now()),
            )
            conn.commit()
            if cur.lastrowid:
                return cur.lastrowid
            # یال از قبل وجود داشته؛ id موجود را برگردان
            cur.execute(
                "SELECT id FROM graph_edges WHERE source_id=? AND target_id=? AND relation_type=?",
                (source_id, target_id, relation_type),
            )
            row = cur.fetchone()
            return row["id"] if row else -1
        finally:
            conn.close()

    def _node_types(self, source_id: int, target_id: int) -> Tuple[str, str]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, node_type FROM graph_nodes WHERE id IN (?, ?)", (source_id, target_id))
            rows = {r["id"]: r["node_type"] for r in cur.fetchall()}
            return rows.get(source_id, "generic"), rows.get(target_id, "generic")
        finally:
            conn.close()

    # -----------------------------------------------------
    # ابزار سطح‌بالا: ساخت نود والد + فرزندان از یک ساختار درختی
    # (منطبق با تصمیم قبلی: محتوای نود والد پارس می‌شود تا با
    #  عنوان نودهای فرزند در دیتابیس تطبیق یابد، بدون infrastructure
    #  سلسله‌مراتبی جداگانه)
    # -----------------------------------------------------
    def link_parent_children(self, parent_title: str, children_titles: List[str]) -> Dict[str, Any]:
        parent = self.find_node_by_title(parent_title)
        if not parent:
            return {"ok": False, "error": f"نود والد '{parent_title}' پیدا نشد."}

        linked = []
        missing = []
        for child_title in children_titles:
            child = self.find_node_by_title(child_title)
            if child:
                self.add_edge(parent["id"], child["id"])
                linked.append(child_title)
            else:
                missing.append(child_title)

        return {"ok": True, "linked": linked, "missing": missing}

    @staticmethod
    def _now() -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("استفاده: python3 graph_builder.py <path_to_db>")
        sys.exit(1)

    gb = GraphBuilder(sys.argv[1])
    print("GraphBuilder آماده شد و schema بررسی/ساخته شد.")
