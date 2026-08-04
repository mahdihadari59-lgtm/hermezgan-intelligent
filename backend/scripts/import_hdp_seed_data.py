from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hdp_v2_embedding_ok.db"
SEED_PATH = ROOT / "scripts" / "seed_hdp_data.json"

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None

def columns(conn: sqlite3.Connection, table: str) -> List[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]

def create_seed_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_seed_records (
        seed_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        category TEXT,
        subcategory TEXT,
        province TEXT,
        county TEXT,
        district TEXT,
        city TEXT,
        latitude REAL,
        longitude REAL,
        source TEXT,
        confidence REAL,
        language TEXT,
        dialect TEXT,
        intent TEXT,
        tags_json TEXT,
        keywords_json TEXT,
        voice_keywords_json TEXT,
        raw_json TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT
    )
    """)

def load_seed_data() -> List[Dict[str, Any]]:
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"Seed file not found: {SEED_PATH}")

    raw = SEED_PATH.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    data = json.loads(raw)
    if isinstance(data, dict):
        if "records" in data and isinstance(data["records"], list):
            return data["records"]
        if "items" in data and isinstance(data["items"], list):
            return data["items"]
        return [data]

    if isinstance(data, list):
        return data

    raise ValueError("Seed JSON must be an object or an array of objects")

def extract_value(seed: Dict[str, Any], names: List[str], default: Any = None) -> Any:
    for name in names:
        if name in seed and seed[name] is not None:
            return seed[name]
    return default

def ensure_knowledge_row(conn: sqlite3.Connection, seed: Dict[str, Any]) -> Optional[int]:
    if not table_exists(conn, "knowledge"):
        return None

    cols = set(columns(conn, "knowledge"))
    title = str(extract_value(seed, ["title", "name", "label"], "") or "").strip()
    content = str(extract_value(seed, ["content", "description", "body", "summary"], "") or "").strip()
    if not title:
        return None

    row = conn.execute(
        "SELECT id FROM knowledge WHERE title = ? LIMIT 1",
        (title,),
    ).fetchone()

    field_map = {
        "title": title,
        "category": extract_value(seed, ["category", "cat", "topic", "type"]),
        "content": content or title,
        "sub_category": extract_value(seed, ["subcategory", "sub_category", "subcat"]),
        "province": extract_value(seed, ["province"]),
        "county": extract_value(seed, ["county"]),
        "district": extract_value(seed, ["district"]),
        "city": extract_value(seed, ["city"]),
        "lat": extract_value(seed, ["latitude", "lat"]),
        "lng": extract_value(seed, ["longitude", "lng", "lon"]),
        "source": extract_value(seed, ["source"]),
        "confidence": extract_value(seed, ["confidence"]),
        "language": extract_value(seed, ["language"]),
        "dialect": extract_value(seed, ["dialect"]),
        "intent": extract_value(seed, ["intent"]),
        "tags_json": json.dumps(extract_value(seed, ["tags"], []), ensure_ascii=False),
        "keywords_json": json.dumps(extract_value(seed, ["keywords"], []), ensure_ascii=False),
        "voice_keywords_json": json.dumps(extract_value(seed, ["voice_keywords"], []), ensure_ascii=False),
        "updated_at": extract_value(seed, ["updated_at"], datetime.now(timezone.utc).date().isoformat()),
        "created_at": extract_value(seed, ["created_at"], datetime.now(timezone.utc).date().isoformat()),
    }

    insert_cols = []
    insert_vals = []
    update_cols = []

    for col, value in field_map.items():
        if col in cols and value is not None:
            insert_cols.append(col)
            insert_vals.append(value)
            if col not in ("id",):
                update_cols.append(col)

    if not insert_cols:
        return None

    if row:
        sets = ", ".join([f"{c}=?" for c in update_cols if c != "title"])
        vals = [field_map[c] for c in update_cols if c != "title"]
        if sets:
            conn.execute(
                f"UPDATE knowledge SET {sets} WHERE id = ?",
                (*vals, row[0]),
            )
        return int(row[0])

    placeholders = ", ".join(["?"] * len(insert_cols))
    conn.execute(
        f"INSERT INTO knowledge ({', '.join(insert_cols)}) VALUES ({placeholders})",
        tuple(insert_vals),
    )
    new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    return int(new_id)

def upsert_seed_record(conn: sqlite3.Connection, seed: Dict[str, Any]) -> None:
    seed_id = str(extract_value(seed, ["id", "seed_id", "external_id"], "") or "").strip()
    title = str(extract_value(seed, ["title", "name", "label"], "") or "").strip()
    content = str(extract_value(seed, ["content", "description", "body", "summary"], "") or "").strip()
    if not seed_id:
        seed_id = title

    payload = json.dumps(seed, ensure_ascii=False)
    now = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        INSERT INTO knowledge_seed_records (
            seed_id, title, content, category, subcategory, province, county, district,
            city, latitude, longitude, source, confidence, language, dialect, intent,
            tags_json, keywords_json, voice_keywords_json, raw_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(seed_id) DO UPDATE SET
            title=excluded.title,
            content=excluded.content,
            category=excluded.category,
            subcategory=excluded.subcategory,
            province=excluded.province,
            county=excluded.county,
            district=excluded.district,
            city=excluded.city,
            latitude=excluded.latitude,
            longitude=excluded.longitude,
            source=excluded.source,
            confidence=excluded.confidence,
            language=excluded.language,
            dialect=excluded.dialect,
            intent=excluded.intent,
            tags_json=excluded.tags_json,
            keywords_json=excluded.keywords_json,
            voice_keywords_json=excluded.voice_keywords_json,
            raw_json=excluded.raw_json,
            updated_at=excluded.updated_at
        """,
        (
            seed_id,
            title,
            content,
            extract_value(seed, ["category", "cat", "topic", "type"]),
            extract_value(seed, ["subcategory", "sub_category", "subcat"]),
            extract_value(seed, ["province"]),
            extract_value(seed, ["county"]),
            extract_value(seed, ["district"]),
            extract_value(seed, ["city"]),
            extract_value(seed, ["latitude", "lat"]),
            extract_value(seed, ["longitude", "lng", "lon"]),
            extract_value(seed, ["source"]),
            extract_value(seed, ["confidence"]),
            extract_value(seed, ["language"]),
            extract_value(seed, ["dialect"]),
            extract_value(seed, ["intent"]),
            json.dumps(extract_value(seed, ["tags"], []), ensure_ascii=False),
            json.dumps(extract_value(seed, ["keywords"], []), ensure_ascii=False),
            json.dumps(extract_value(seed, ["voice_keywords"], []), ensure_ascii=False),
            payload,
            now,
            now,
        ),
    )

def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(DB_PATH)

    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
        create_seed_table(conn)

    seeds = load_seed_data()
    if not seeds:
        print("No seed records found.")
        return

    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")

        create_seed_table(conn)

        imported = 0
        knowledge_rows = 0

        for seed in seeds:
            if not isinstance(seed, dict):
                continue
            upsert_seed_record(conn, seed)
            kid = ensure_knowledge_row(conn, seed)
            if kid is not None:
                knowledge_rows += 1
            imported += 1

        conn.commit()

    print(f"IMPORTED={imported}")
    print(f"KNOWLEDGE_ROWS={knowledge_rows}")

if __name__ == "__main__":
    main()
