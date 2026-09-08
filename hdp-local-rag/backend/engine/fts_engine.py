# engine/fts_engine.py
from core.sqlite_service import db
from engine.base_engine import BaseEngine


class FTSEngine(BaseEngine):

    def __init__(self, db_path):
        super().__init__(
            name="fts",
            weight=...
        )

        self.db_path = db_path

    def search(self, query, context=None):

        sql = """
        SELECT
            k.id,
            k.title,
            k.content,
            bm25(knowledge_fts) AS score
        FROM knowledge_fts
        JOIN knowledge k
        ON knowledge_fts.rowid = k.id
        WHERE knowledge_fts MATCH ?
        ORDER BY score
        LIMIT 20
        """

        try:
            rows = db.execute(sql, (query,))
        except Exception:
            return []

        results = []

        for row in rows:

            score = 1.0 / (1.0 + abs(row["score"]))

            results.append(
                self.build_result(
                    doc_id=row["id"],
                    score=score,
                    title=row["title"],
                    content=row["content"][:300]
                )
            )

        return results
