import sqlite3
from engine.base_engine import BaseEngine


class IntentEngine(BaseEngine):

    def __init__(self, db_path):
        super().__init__(
            name="intent",
            weight=1.0
        )

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

    def search(self, query, context=None):

        sql = """
        SELECT
            intent_name,
            confidence,
            pattern
        FROM intent_patterns
        """

        self.cur.execute(sql)
        rows = self.cur.fetchall()

        query = query.strip()

        best = None

        for row in rows:

            if row["pattern"] in query:

                if best is None:

                    best = row

                elif row["confidence"] > best["confidence"]:

                    best = row

        if best is None:

            return []

        return [
            self.build_result(
                doc_id=0,
                score=best["confidence"],
                title=best["intent_name"],
                content=best["pattern"],
                metadata={
                    "intent": best["intent_name"]
                }
            )
        ]

    def close(self):
        self.conn.close()
