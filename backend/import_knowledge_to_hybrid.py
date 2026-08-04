import sqlite3
import json
from pathlib import Path

DB_PATH = "hdp_v2.db"
OUT_PATH = Path("data/knowledge_base.json")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT id, title, content, category, category_fa, keywords, tags,
           topic, city, lat, lon, source, priority
    FROM knowledge
    WHERE (is_deleted IS NULL OR is_deleted = 0)
      AND (status IS NULL OR status = 'active')
""")
rows = cur.fetchall()
conn.close()

# دیدوپ بر اساس عنوان - رکورد با priority بالاتر می‌مونه
best_by_title = {}
for r in rows:
    title = (r["title"] or "").strip()
    if not title:
        continue
    prio = r["priority"] or 1
    existing = best_by_title.get(title)
    if existing is None or prio > (existing["priority"] or 1):
        best_by_title[title] = r

documents = []
categories = {}

for title, r in best_by_title.items():
    doc_id = f"kb_{r['id']}"
    category = r["category"] or "general"

    doc = {
        "id": doc_id,
        "title": title,
        "content": r["content"] or "",
        "metadata": {
            "category_fa": r["category_fa"] or "",
            "keywords": r["keywords"] or "",
            "tags": r["tags"] or "",
            "topic": r["topic"] or "",
            "city": r["city"] or "",
            "lat": r["lat"],
            "lon": r["lon"],
            "source": r["source"] or "",
        },
        "category": category,
        "created_at": None,
    }
    documents.append(doc)
    categories.setdefault(category, []).append(doc_id)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump({"documents": documents, "categories": categories}, f, ensure_ascii=False, indent=2)

print(f"✅ {len(documents)} سند از {len(rows)} رکورد خام وارد شد → {OUT_PATH}")
print(f"✅ {len(categories)} دسته‌بندی")
