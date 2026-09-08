from collections import defaultdict

# منابع اصلی برای اولویت‌بندی
# اصلاح شد: "fts5" -> "fts" (تایپو که باعث می‌شد نتایج FTS همیشه از پاسخ
# نهایی حذف شوند)؛ "hybrid" و "synonym" اضافه شدند (قبلاً هیچ‌وقت به‌عنوان
# منبع اصلی در نظر گرفته نمی‌شدند)؛ "vector" برای زیرساخت آینده اضافه شد.
PRIMARY_SOURCES = {
    "graph",
    "fts",
    "hybrid",
    "vector",
    "medical",
    "traffic",
    "tourism",
    "legal",
    "synonym"
}

# آستانه‌های پاسخ مستقیم (کمی پایین‌تر برای پاسخ‌دهی بهتر)
AUTO_ANSWER_SCORE = 2.2
AUTO_ANSWER_GAP = 0.5


class AnswerEngine:

    def build(self, query, results):

        if not results:
            return {
                "answer": "نتیجه‌ای پیدا نشد.",
                "items": []
            }

        # اولویت با موتورهای اصلی
        primary = [
            r for r in results
            if r["source"] in PRIMARY_SOURCES
        ]

        if not primary:
            primary = results

        # مرتب‌سازی اولیه بر اساس امتیاز (نزولی)
        primary.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        # حذف نتایج تکراری بر اساس id یا ترکیب title + content
        unique = {}
        for r in primary:
            if r.get("id"):
                key = r.get("id")
            else:
                key = (
                    r.get("title", ""),
                    r.get("content", "")
                )

            if key not in unique:
                unique[key] = r
            elif r.get("score", 0) > unique[key].get("score", 0):
                unique[key] = r

        primary = list(unique.values())

        primary.sort(
            key=lambda x: x.get("score", 0),
            reverse=True
        )

        if len(primary) == 1:
            r = primary[0]
            return {
                "answer": r.get("content") or r["title"],
                "items": primary
            }

        first = primary[0]
        second = primary[1] if len(primary) > 1 else None

        query_clean = query.strip().lower()
        title_clean = str(first.get("title") or "").strip().lower()
        content_clean = str(first.get("content") or "").lower()

        is_relevant = (
            query_clean
            and (
                (title_clean and (query_clean in title_clean or title_clean in query_clean))
                or (content_clean and query_clean in content_clean)
            )
        )

        is_primary_source = first.get("source") in PRIMARY_SOURCES
        second_is_weak = (
            second is None
            or second.get("source") in ("intent", "synonym")
        )

        if first.get("content") and is_primary_source and second_is_weak:
            return {
                "answer": first["content"],
                "items": [
                    r for r in primary[:5]
                    if r["source"] not in ("intent", "synonym")
                ]
            }

        if first.get("content") and is_relevant:

            if first.get("score", 0) >= AUTO_ANSWER_SCORE:
                return {
                    "answer": first["content"],
                    "items": [
                        r for r in primary[:5]
                        if r["source"] not in ("intent", "synonym")
                    ]
                }

            if (
                second is not None
                and first.get("score", 0) >= second.get("score", 0) + AUTO_ANSWER_GAP
            ):
                return {
                    "answer": first["content"],
                    "items": [
                        r for r in primary[:5]
                        if r["source"] not in ("intent", "synonym")
                    ]
                }

        groups = defaultdict(list)

        for r in primary:
            title = r.get("title", "بدون عنوان")
            groups[title].append(r)

        names = list(groups.keys())

        answer = (
            f"برای «{query}» "
            f"{len(names)} مورد پیدا شد:\n\n"
        )

        for name in names[:10]:
            answer += f"• {name}\n"

        answer += "\nلطفاً یکی از موارد بالا را انتخاب کنید."

        return {
            "answer": answer,
            "items": primary[:10]
        }
