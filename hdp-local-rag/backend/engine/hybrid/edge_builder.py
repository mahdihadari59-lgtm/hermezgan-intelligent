#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/edge_builder.py
-------------------------------------------------------
لایه اتوماسیون برای ساخت یال‌های گراف — برخلاف
GraphBuilder.add_edge (که یال بین دو id مشخص می‌سازد)، این فایل
مسئول پیدا کردن نودهایی است که *باید* به هم وصل شوند اما هنوز
یالی ندارند (مثلاً چون از منابع/زمان‌های متفاوت اضافه شده‌اند).

استراتژی فعلی (ساده و شفاف؛ در آینده قابل تعویض با embedding
similarity واقعی):
    - هم‌دامنه‌بودن (domain یکسان) شرط لازم است.
    - هم‌پوشانی کلمات کلیدی عنوان/محتوا بالای آستانه معین.
    - relation_type/weight نهایی از GraphBuilder.resolve_relation
      خوانده می‌شود (نه اینجا هارد-کد).
-------------------------------------------------------
"""

import sqlite3
from typing import Optional, List, Dict, Tuple
from itertools import combinations

from engine.hybrid.config import HybridConfig
from engine.hybrid.graph_builder import GraphBuilder
from engine.hybrid.utils import normalize_persian, tokenize


class EdgeBuilder:
    def __init__(self, db_path: Optional[str] = None, graph_builder: Optional[GraphBuilder] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        self.graph_builder = graph_builder or GraphBuilder(self.db_path, seed_default_rules=False)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _token_overlap(self, tokens_a: set, tokens_b: set) -> float:
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        return len(intersection) / len(union) if union else 0.0

    def auto_link_by_domain(
        self,
        domain: str,
        min_overlap: float = 0.2,
        max_new_edges: int = 200,
    ) -> Dict[str, int]:
        """
        در یک دامنه مشخص، همه جفت‌نودها را بررسی می‌کند و اگر
        هم‌پوشانی کلمات کلیدی‌شان از آستانه بیشتر بود، یال می‌سازد.
        هزینه این عملیات O(n^2) است؛ برای دامنه‌های بزرگ (چند هزار
        نود) باید با یک پیش‌فیلتر (مثلا shared keyword index) بهینه شود.
        """
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, content FROM graph_nodes WHERE domain = ?", (domain,)
            )
            nodes = cur.fetchall()
        finally:
            conn.close()

        node_tokens: Dict[int, set] = {}
        for node in nodes:
            text = f"{node['title'] or ''} {node['content'] or ''}"
            node_tokens[node["id"]] = set(tokenize(normalize_persian(text)))

        created = 0
        checked = 0
        for (id_a, tokens_a), (id_b, tokens_b) in combinations(node_tokens.items(), 2):
            checked += 1
            overlap = self._token_overlap(tokens_a, tokens_b)
            if overlap >= min_overlap:
                self.graph_builder.add_edge(id_a, id_b)
                created += 1
                if created >= max_new_edges:
                    break

        return {"domain": domain, "checked_pairs": checked, "edges_created_or_existing": created}

    def auto_link_all_domains(self, domains: List[str], min_overlap: float = 0.2) -> List[Dict[str, int]]:
        return [self.auto_link_by_domain(d, min_overlap=min_overlap) for d in domains]

    def find_isolated_nodes(self) -> List[Dict]:
        """نودهایی که هیچ یالی ندارند — کاندیدای بررسی دستی یا auto_link."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, domain FROM graph_nodes "
                "WHERE id NOT IN (SELECT source_id FROM graph_edges) "
                "AND id NOT IN (SELECT target_id FROM graph_edges)"
            )
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="HDP Edge Builder")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--min-overlap", type=float, default=0.2)
    args = parser.parse_args()

    eb = EdgeBuilder()
    result = eb.auto_link_by_domain(args.domain, min_overlap=args.min_overlap)
    print(json.dumps(result, ensure_ascii=False, indent=2))
