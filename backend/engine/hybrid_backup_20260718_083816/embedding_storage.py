#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
engine/hybrid/embedding_storage.py
-------------------------------------------------------
لایه ذخیره‌سازی بردار (embedding/vector) برای نودهای گراف.

طراحی برای سبک ماندن روی Termux:
    - بردارها به‌صورت JSON (لیست float) در SQLite ذخیره می‌شوند،
      نه numpy array یا فرمت باینری پیچیده.
    - محاسبه cosine similarity با پایتون خالص (بدون numpy).
    - چند "model" مختلف می‌تواند هم‌زمان ذخیره شود (مثلا "tfidf"
      امروز، و بعداً "sentence_embedding" وقتی مدل سبک‌تری اضافه شد)
      بدون تداخل، چون model_name بخشی از کلید است.
-------------------------------------------------------
"""

import sqlite3
import json
import math
from typing import Optional, List, Dict, Tuple

from .config import HybridConfig

class EmbeddingStorage:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or HybridConfig.DB_PATH
        HybridConfig.ensure_data_dir()
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    node_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    vector_json TEXT NOT NULL,
                    dim INTEGER NOT NULL,
                    updated_at TEXT,
                    PRIMARY KEY (node_id, model_name)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    # -----------------------------------------------------
    # ذخیره / بازیابی
    # -----------------------------------------------------
    def save(self, node_id: int, vector, model_name: str = "default") -> None:
        """
        @param vector: لیست float یا dict{term: weight} (بردار sparse).
                       هر دو به‌صورت JSON ذخیره می‌شوند و در بازیابی
                       فرمت اصلی حفظ می‌شود.
        """
        if hasattr(vector, "tolist"):
            vector = vector.tolist()

        payload = json.dumps(vector, ensure_ascii=False)
        dim = len(vector)
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO embeddings (node_id, model_name, vector_json, dim, updated_at) "
                "VALUES (?, ?, ?, ?, datetime('now')) "
                "ON CONFLICT(node_id, model_name) DO UPDATE SET "
                "vector_json=excluded.vector_json, dim=excluded.dim, updated_at=excluded.updated_at",
                (node_id, model_name, payload, dim),
            )
            conn.commit()
        finally:
            conn.close()

    def save_many(self, vectors: Dict[int, object], model_name: str = "default") -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            rows = [
                (node_id, model_name, json.dumps(vec, ensure_ascii=False), len(vec))
                for node_id, vec in vectors.items()
            ]
            cur.executemany(
                "INSERT INTO embeddings (node_id, model_name, vector_json, dim, updated_at) "
                "VALUES (?, ?, ?, ?, datetime('now')) "
                "ON CONFLICT(node_id, model_name) DO UPDATE SET "
                "vector_json=excluded.vector_json, dim=excluded.dim, updated_at=excluded.updated_at",
                rows,
            )
            conn.commit()
        finally:
            conn.close()

    def get(self, node_id: int, model_name: str = "default"):
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT vector_json FROM embeddings WHERE node_id=? AND model_name=?",
                (node_id, model_name),
            )
            row = cur.fetchone()
            return json.loads(row["vector_json"]) if row else None
        finally:
            conn.close()

    def get_all(self, model_name: str = "default") -> Dict[int, object]:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT node_id, vector_json FROM embeddings WHERE model_name=?", (model_name,))
            return {row["node_id"]: json.loads(row["vector_json"]) for row in cur.fetchall()}
        finally:
            conn.close()

    def delete(self, node_id: int, model_name: str = "default") -> None:
        conn = self._connect()
        try:
            conn.execute(
                "DELETE FROM embeddings WHERE node_id=? AND model_name=?", (node_id, model_name)
            )
            conn.commit()
        finally:
            conn.close()

    # نام جایگزین برای delete — برای هم‌خوانی با نام‌گذاری‌ای که در
    # بخش‌های دیگر پروژه (یا نسخه‌های موازی) استفاده شده است.
    def remove_embedding(self, node_id: int, model_name: str = "default") -> None:
        self.delete(node_id, model_name=model_name)

    def get_all_nodes(self, model_name: str = "default") -> List[int]:
        """فقط لیست node_id هایی که برای این model بردار ذخیره‌شده دارند."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute("SELECT node_id FROM embeddings WHERE model_name=?", (model_name,))
            return [row["node_id"] for row in cur.fetchall()]
        finally:
            conn.close()

    def stats(self) -> Dict[str, object]:
        """آمار کلی جدول embeddings: تعداد بردار به تفکیک model و ابعاد میانگین."""
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT model_name, COUNT(*) AS cnt, AVG(dim) AS avg_dim FROM embeddings GROUP BY model_name"
            )
            by_model = {
                row["model_name"]: {"count": row["cnt"], "avg_dim": round(row["avg_dim"] or 0, 2)}
                for row in cur.fetchall()
            }
            cur.execute("SELECT COUNT(*) AS total FROM embeddings")
            total = cur.fetchone()["total"]
            return {"total": total, "by_model": by_model}
        finally:
            conn.close()

    # -----------------------------------------------------
    # شباهت — پشتیبانی از هر دو نوع بردار: dense (list) و sparse (dict)
    # -----------------------------------------------------
    @staticmethod
    def cosine_similarity(v1, v2) -> float:
        if isinstance(v1, dict) or isinstance(v2, dict):
            return EmbeddingStorage._cosine_sparse(v1, v2)
        return EmbeddingStorage._cosine_dense(v1, v2)

    @staticmethod
    def _cosine_dense(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    @staticmethod
    def _cosine_sparse(v1: Dict[str, float], v2: Dict[str, float]) -> float:
        if not v1 or not v2:
            return 0.0
        common_keys = set(v1.keys()) & set(v2.keys())
        dot = sum(v1[k] * v2[k] for k in common_keys)
        norm1 = math.sqrt(sum(w * w for w in v1.values()))
        norm2 = math.sqrt(sum(w * w for w in v2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def search_similar(
        self, query_vector, model_name: str = "default", top_k: int = 10, exclude_node_id: Optional[int] = None
    ) -> List[Tuple[int, float]]:
        """جستجوی شباهت برداری روی همه بردارهای ذخیره‌شده یک model."""
        all_vectors = self.get_all(model_name)
        scored = []
        for node_id, vec in all_vectors.items():
            if exclude_node_id is not None and node_id == exclude_node_id:
                continue
            sim = self.cosine_similarity(query_vector, vec)
            if sim > 0:
                scored.append((node_id, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
