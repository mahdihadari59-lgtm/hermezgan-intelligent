#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/node_features.py
-------------------------------------------------------
استخراج بردار ویژگی عددی (feature vector) برای هر نود گراف —
پیش‌نیاز لازم برای GAT (Graph Attention Network) و هر مدل
یادگیری ماشین دیگری که بعداً روی گراف اجرا شود.

ویژگی‌هایی که استخراج می‌شود (فعلاً همه با پایتون خالص، بدون
نیاز به embedding معنایی سنگین):
    - طول عنوان و محتوا (نرمال‌شده)
    - one-hot دامنه (domain)
    - one-hot نوع نود (node_type)
    - درجه گراف (تعداد یال‌های ورودی/خروجی)
    - امتیاز PageRank (اگر از قبل محاسبه شده باشد)

بردار نهایی در embedding_storage با model_name="node_features"
ذخیره می‌شود تا هم برای رتبه‌بندی و هم بعداً به‌عنوان ورودی
gat_model.py قابل استفاده باشد.
-------------------------------------------------------
"""

import sqlite3
from typing import Dict, List, Optional

from engine.hybrid.config import HybridConfig
from engine.hybrid.constants import DOMAINS, NODE_TYPES, EMBEDDING_MODEL_FEATURES, EMBEDDING_MODEL_PAGERANK
from engine.hybrid.embedding_storage import EmbeddingStorage
from engine.hybrid.utils import normalize_persian


class NodeFeatureExtractor:
    def __init__(self, db_path: Optional[str] = None, storage: Optional[EmbeddingStorage] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        self.storage = storage or EmbeddingStorage(self.db_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _degree_map(self, conn: sqlite3.Connection) -> Dict[int, int]:
        cur = conn.cursor()
        cur.execute(
            "SELECT node_id, COUNT(*) AS degree FROM ("
            "  SELECT source_id AS node_id FROM graph_edges "
            "  UNION ALL "
            "  SELECT target_id AS node_id FROM graph_edges"
            ") GROUP BY node_id"
        )
        return {row["node_id"]: row["degree"] for row in cur.fetchall()}

    def extract_one(self, node_row: sqlite3.Row, degree: int, pagerank_score: float) -> List[float]:
        title_len = len(normalize_persian(node_row["title"] or ""))
        content_len = len(normalize_persian(node_row["content"] or ""))

        domain_one_hot = [1.0 if node_row["domain"] == d else 0.0 for d in DOMAINS]
        type_one_hot = [1.0 if node_row["node_type"] == t else 0.0 for t in NODE_TYPES]

        # نرمال‌سازی ساده طول‌ها با یک سقف نرم تا مقیاس بردار منفجر نشه
        normalized_title_len = min(1.0, title_len / 100.0)
        normalized_content_len = min(1.0, content_len / 500.0)
        normalized_degree = min(1.0, degree / 20.0)

        return (
            [normalized_title_len, normalized_content_len, normalized_degree, pagerank_score]
            + domain_one_hot
            + type_one_hot
        )

    def build_all(self) -> Dict[str, int]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, title, content, node_type, domain FROM graph_nodes")
            nodes = cur.fetchall()
            degrees = self._degree_map(conn)
        finally:
            conn.close()

        pagerank_vectors = self.storage.get_all(model_name=EMBEDDING_MODEL_PAGERANK)

        vectors: Dict[int, List[float]] = {}
        for node in nodes:
            degree = degrees.get(node["id"], 0)
            pr_score = pagerank_vectors.get(node["id"], [0.0])[0]
            vectors[node["id"]] = self.extract_one(node, degree, pr_score)

        self.storage.save_many(vectors, model_name=EMBEDDING_MODEL_FEATURES)
        return {"n_nodes": len(vectors), "feature_dim": len(next(iter(vectors.values()))) if vectors else 0}

    def get(self, node_id: int) -> Optional[List[float]]:
        return self.storage.get(node_id, model_name=EMBEDDING_MODEL_FEATURES)


if __name__ == "__main__":
    import json

    extractor = NodeFeatureExtractor()
    stats = extractor.build_all()
    print(json.dumps(stats, ensure_ascii=False, indent=2))
