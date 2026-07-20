#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/graph_features.py
-------------------------------------------------------
لایه تجمیع نهایی: ترکیب node_features + pagerank + ساختار
همسایگی گراف در یک خروجی واحد، آماده برای:
    1) مصرف مستقیم توسط hybrid_ranker (سیگنال اضافه امتیازدهی)
    2) ورودی آینده gat_model.py / trainer.py (وقتی فاز ML شروع شود)

این فایل خودش هیچ محاسبه سنگینی انجام نمی‌دهد؛ فقط خروجی
node_features.py و pagerank.py را می‌خواند و به همراه لیست
همسایگی (adjacency) در قالب یکسان بسته‌بندی می‌کند — دقیقاً
فرمتی که یک GAT سبک (پیاده‌سازی numpy-only در آینده) نیاز دارد:
    {
        "node_ids": [...],
        "features": [[...], [...], ...],
        "edges": [(i, j), ...]   # اندیس‌های محلی، نه id واقعی گراف
    }
-------------------------------------------------------
"""

import sqlite3
from typing import Optional, Dict, List, Tuple

from engine.hybrid.config import HybridConfig
from engine.hybrid.constants import EMBEDDING_MODEL_FEATURES, EMBEDDING_MODEL_PAGERANK
from engine.hybrid.embedding_storage import EmbeddingStorage
from engine.hybrid.node_features import NodeFeatureExtractor
from engine.hybrid.pagerank import PageRankEngine


class GraphFeatureBuilder:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        self.storage = EmbeddingStorage(self.db_path)
        self.feature_extractor = NodeFeatureExtractor(self.db_path, storage=self.storage)
        self.pagerank_engine = PageRankEngine(self.db_path, storage=self.storage)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def refresh_all(self) -> Dict[str, int]:
        """اجرای کامل pipeline: PageRank → Node Features (که به pagerank وابسته است)."""
        self.pagerank_engine.compute_and_store()
        return self.feature_extractor.build_all()

    def build_training_snapshot(self, domain: Optional[str] = None) -> Dict:
        """
        خروجی آماده برای مصرف مدل گراف (GAT یا مشابه).
        اگر domain داده شود، فقط زیرگراف همان دامنه برمی‌گردد.
        """
        conn = self._connect()
        try:
            cur = conn.cursor()
            if domain:
                cur.execute("SELECT id FROM graph_nodes WHERE domain = ?", (domain,))
            else:
                cur.execute("SELECT id FROM graph_nodes")
            node_ids = [row["id"] for row in cur.fetchall()]
            id_to_index = {node_id: idx for idx, node_id in enumerate(node_ids)}

            cur.execute("SELECT source_id, target_id FROM graph_edges")
            edges: List[Tuple[int, int]] = []
            for row in cur.fetchall():
                s, t = row["source_id"], row["target_id"]
                if s in id_to_index and t in id_to_index:
                    edges.append((id_to_index[s], id_to_index[t]))
        finally:
            conn.close()

        feature_vectors = self.storage.get_all(model_name=EMBEDDING_MODEL_FEATURES)
        features = [feature_vectors.get(node_id, []) for node_id in node_ids]

        return {
            "node_ids": node_ids,
            "features": features,
            "edges": edges,
            "n_nodes": len(node_ids),
            "n_edges": len(edges),
            "feature_dim": len(features[0]) if features and features[0] else 0,
        }

    def node_summary(self, node_id: int) -> Dict:
        """خلاصه همه سیگنال‌های یک نود — مفید برای دیباگ یا نمایش در پنل."""
        return {
            "id": node_id,
            "pagerank": self.pagerank_engine.get_score(node_id),
            "features": self.feature_extractor.get(node_id),
        }


if __name__ == "__main__":
    import json

    builder = GraphFeatureBuilder()
    stats = builder.refresh_all()
    print(json.dumps({"refresh": stats}, ensure_ascii=False, indent=2))
    snapshot = builder.build_training_snapshot()
    print(json.dumps({"n_nodes": snapshot["n_nodes"], "n_edges": snapshot["n_edges"], "feature_dim": snapshot["feature_dim"]}, ensure_ascii=False, indent=2))
