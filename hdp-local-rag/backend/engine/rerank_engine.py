class ReRankEngine:
    """
    نسخه سبک ReRank برای HDP
    """

    # اصلاح شد: "fts5" -> "fts" (این تایپو باعث می‌شد بونوس FTS هیچ‌وقت
    # اعمال نشود، چون FTSEngine واقعاً با name="fts" ثبت می‌شود نه "fts5").
    # "hybrid" و "vector" صریحاً اضافه شدند (قبلاً به‌طور ضمنی صفر می‌گرفتند
    # از طریق .get(source, 0) — همان مقدار، فقط الان مستند و صریح است؛
    # این عدد یک placeholder خنثی است، نه تصمیم کسب‌وکاری جدید).
    SOURCE_BONUS = {
        "graph": 2.5,
        "fts": 2.0,
        "hybrid": 0.0,
        "vector": 0.0,
        "medical": 2.0,
        "traffic": 2.0,
        "tourism": 2.0,
        "legal": 2.0,
        "intent": -1.0,
        "synonym": -2.0,
    }

    def rerank(self, query, results):

        if not results:
            return []

        words = query.strip().lower().split()

        reranked = []

        for r in results:

            score = float(r.get("score", 0))

            title = (r.get("title") or "").lower()
            content = (r.get("content") or "").lower()
            source = r.get("source", "")

            score += self.SOURCE_BONUS.get(source, 0)

            if title == query.lower():
                score += 6

            elif title.startswith(query.lower()):
                score += 4

            elif query.lower() in title:
                score += 3

            if query.lower() in content:
                score += 2

            for w in words:
                if w in title:
                    score += 0.40
                elif w in content:
                    score += 0.20

            item = dict(r)
            item["score"] = round(score, 3)

            reranked.append(item)

        reranked.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return reranked
