#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.sqlite_service import db
from engine.base_engine import BaseEngine


class GraphSearchEngineV2(BaseEngine):

    def __init__(self):

        super().__init__(
            name="graph_v2",
            weight=1.20
        )

    # --------------------------------------------------

    def find_root(self, query):

        sql = """
        SELECT
            id,
            title,
            category,
            content,
            city,
            keywords
        FROM knowledge
        WHERE
            title LIKE ?
            OR keywords LIKE ?
            OR content LIKE ?
        LIMIT 20
        """

        return db.execute_query(
            sql,
            (
                f"%{query}%",
                f"%{query}%",
                f"%{query}%"
            )
        )

    # --------------------------------------------------

    def get_neighbors(self, node_id):

        sql = """
        SELECT
            target_id,
            relation,
            confidence
        FROM knowledge_links
        WHERE source_id=?
        """

        return db.execute_query(sql, (node_id,))

    # --------------------------------------------------

    def search(self, query, context=None):

        roots = self.find_root(query)

        results = []

        visited = set()

        for row in roots:

            root_id = row["id"]

            visited.add(root_id)

            # خود نود اصلی
            results.append(

                self.build_result(

                    doc_id=root_id,

                    score=1.0,

                    title=row["title"],

                    content=row["content"][:300],

                    metadata={
                        "category": row["category"],
                        "city": row["city"],
                        "graph": True,
                        "hop": 0
                    }

                )

            )

            # -------------------------
            # همسایه‌های مستقیم
            # -------------------------

            neighbors = self.get_neighbors(root_id)

            for n in neighbors:

                target_id = n["target_id"]

                if target_id in visited:
                    continue

                visited.add(target_id)

                sql = """
                SELECT
                    id,
                    title,
                    category,
                    content,
                    city
                FROM knowledge
                WHERE id=?
                """

                rows = db.execute_query(sql, (target_id,))

                if not rows:
                    continue

                node = rows[0]

                results.append(

                    self.build_result(

                        doc_id=node["id"],

                        score=0.6,

                        title=node["title"],

                        content=node["content"][:300],

                        metadata={
                            "category": node["category"],
                            "city": node["city"],
                            "graph": True,
                            "hop": 1,
                            "relation": n["relation"]
                        }

                    )

                )

        return results
