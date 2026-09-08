import sqlite3
import os

MASTER_DB = "data/master/master_dataset.db"
OUTPUT_DB = "data/production/hormozgan_v2.db"

if os.path.exists(OUTPUT_DB):
    os.remove(OUTPUT_DB)

src = sqlite3.connect(MASTER_DB)
dst = sqlite3.connect(OUTPUT_DB)

dst.execute("""
CREATE TABLE hormozgan_knowledge (
    id INTEGER PRIMARY KEY,
    title TEXT,
    original_title TEXT,
    content TEXT,
    category TEXT,
    keywords TEXT,
    source TEXT,
    views INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
""")

dst.execute("""
CREATE VIRTUAL TABLE hormozgan_fts
USING fts5(
    title,
    content,
    category
)
""")

rows = src.execute("""
SELECT id,title,content,category
FROM knowledge
""").fetchall()

for row in rows:
    dst.execute("""
    INSERT INTO hormozgan_knowledge(
        id,title,original_title,
        content,category,
        keywords,source,
        created_at,updated_at
    )
    VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        row[0],
        row[1],
        row[1],
        row[2],
        row[3],
        "",
        "master_dataset",
        "",
        ""
    ))

    dst.execute("""
    INSERT INTO hormozgan_fts(
        rowid,title,content,category
    )
    VALUES(?,?,?,?)
    """,(
        row[0],
        row[1],
        row[2],
        row[3]
    ))

dst.commit()

print("Imported:", len(rows))

src.close()
dst.close()
