import sqlite3
from engine.base_engine import BaseEngine


class SynonymEngine(BaseEngine):

    def __init__(self, db_path):
        super().__init__(
            name="synonym",
            weight=0.90
        )

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def search(self, query, context=None):
        words = query.split()
        found = []
        seen = set()

        for word in words:
            sql = """
            SELECT *
            FROM knowledge_synonyms
            WHERE term=?
               OR synonym=?
            """

            rows = self.execute(sql, (word, word))

            for row in rows:
                if row["term"] == word:
                    replacement = row["synonym"]
                else:
                    replacement = row["term"]

                # حذف نتایج تکراری
                if replacement in seen:
                    continue

                seen.add(replacement)

                found.append(
                    self.build_result(
                        doc_id=0,
                        score=row["weight"] / 10.0,
                        title=replacement,
                        content=replacement,
                        metadata={
                            "original": word,
                            "replacement": replacement
                        }
                    )
                )

        return found

    def execute(self, sql, params=()):
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def close(self):
        self.conn.close()
