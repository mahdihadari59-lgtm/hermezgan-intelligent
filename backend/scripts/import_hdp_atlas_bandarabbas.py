from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hdp_v2_embedding_ok.db"
ATLAS_PATH = ROOT / "scripts" / "seed_hdp_atlas_bandarabbas.json"

def slugify_fa(text: str) -> str:
    return (
        text.replace(" ", "_")
            .replace("(", "")
            .replace(")", "")
            .replace("،", "")
            .replace("/", "_")
            .replace("-", "_")
            .replace("ـ", "_")
    )

def ensure_tables(conn: sqlite3.Connection) -> None:
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
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")

def upsert_seed_record(conn: sqlite3.Connection, seed_id: str, title: str, content: str, category: str, subcategory: str, province: str, county: str, district: str, city: str, latitude: Any, longitude: Any, source: str, confidence: Any, language: str, dialect: str, intent: str, tags: List[str], keywords: List[str], voice_keywords: List[str], raw: Dict[str, Any]) -> None:
    now = datetime.now(timezone.utc).isoformat()

    raw = raw or {}
    tags = tags or []
    keywords = keywords or tags or []
    voice_keywords = voice_keywords or []
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
            seed_id, title, content, category, subcategory, province, county, district,
            city, latitude, longitude, source, confidence, language, dialect, intent,
            json.dumps(tags, ensure_ascii=False),
            json.dumps(keywords, ensure_ascii=False),
            json.dumps(voice_keywords, ensure_ascii=False),
            json.dumps(raw, ensure_ascii=False),
            now, now,
        ),
    )




def add_knowledge_row(
    conn: sqlite3.Connection,
    seed_id: str,
    title: str,
    content: str,
    category: str,
    subcategory: str,
    province: Any,
    county: Any,
    district: Any,
    city: Any,
    latitude: Any,
    longitude: Any,
    tags: List[str] = None,
    keywords: List[str] = None,
    raw: Dict[str, Any] = None,
) -> int:
    now = datetime.now(timezone.utc).isoformat()

    raw = raw or {}
    tags = tags or []
    keywords = keywords or tags or []

    def _scalar(v):
        if isinstance(v, (list, tuple)):
            return v[0] if v else None
        return v

    def _text(v):
        v = _scalar(v)
        if v is None:
            return None
        return str(v).strip()

    def _num(v):
        v = _scalar(v)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            return None

    title = _text(title) or ""
    content = _text(content) or ""
    category = _text(category) or ""
    subcategory = _text(subcategory) or ""
    province = _text(province)
    county = _text(county)
    district = _text(district)
    city = _text(city) or ""
    latitude = _num(latitude)
    longitude = _num(longitude)

    tags_text = ", ".join([str(x).strip() for x in tags if str(x).strip()])
    keywords_text = ", ".join([str(x).strip() for x in keywords if str(x).strip()])

    atlas_text = ""
    if isinstance(raw, dict):
        atlas_text = str(raw.get("عنوان") or raw.get("name") or raw.get("title") or "")

    intent_text = ""
    if isinstance(raw, dict):
        intent_text = str(raw.get("intent") or raw.get("main_intent") or raw.get("sub_intent") or "")

    entity_type_text = str(category or "knowledge")

    row = conn.execute(
        "SELECT id FROM knowledge WHERE title = ? LIMIT 1",
        (title,),
    ).fetchone()

    if row:
        kid = int(row[0])
        conn.execute(
            """
            UPDATE knowledge
            SET content=?,
                category=?,
                subcategory=?,
                city=?,
                lat=?,
                lon=?,
                tags=?,
                keywords=?,
                source=?,
                confidence=?,
                atlas=?,
                intent=?,
                entity_type=?,
                updated_at=?
            WHERE id=?
            """,
            (
                content,
                category,
                subcategory,
                city,
                latitude,
                longitude,
                tags_text,
                keywords_text,
                raw.get("source"),
                raw.get("confidence"),
                atlas_text,
                intent_text,
                entity_type_text,
                now,
                kid,
            ),
        )
        return kid

    conn.execute(
        """
        INSERT INTO knowledge (
            title,
            category,
            content,
            subcategory,
            city,
            lat,
            lon,
            tags,
            keywords,
            source,
            confidence,
            atlas,
            intent,
            entity_type,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            category,
            content,
            subcategory,
            city,
            latitude,
            longitude,
            tags_text,
            keywords_text,
            raw.get("source"),
            raw.get("confidence"),
            atlas_text,
            intent_text,
            entity_type_text,
            now,
            now,
        ),
    )
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])

def walk_items(node: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Dict[str, Any]]]:
    items: List[Tuple[str, Dict[str, Any]]] = []
    for key, value in node.items():
        if not isinstance(value, dict):
            continue
        if key in {"موقعیت_شهر", "جدول_جمع‌بندی_و_مقایسه", "نقاط_مرجع_عمومی_منطقه"}:
            continue
        if key.startswith("محله_") or key.startswith("شهرک_"):
            items.append((key, value))
    return items


def walk_items(node: Dict[str, Any], prefix: str = "") -> List[Tuple[str, Dict[str, Any]]]:
    items: List[Tuple[str, Dict[str, Any]]] = []
    for key, value in node.items():
        if not isinstance(value, dict):
            continue
        if key in {"موقعیت_شهر", "جدول_جمع‌بندی_و_مقایسه", "نقاط_مرجع_عمومی_منطقه"}:
            continue
        if key.startswith("محله_") or key.startswith("شهرک_"):
            items.append((key, value))
    return items

def import_atlas() -> None:
    raw = json.loads(ATLAS_PATH.read_text(encoding="utf-8"))
    atlas = raw["اطلس_شهرک‌ها_و_محله‌های_بندرعباس"]

    with sqlite3.connect(str(DB_PATH)) as conn:
        ensure_tables(conn)

        # atlas record
        atlas_seed_id = "ATLAS_BANDARABBAS_001"
        upsert_seed_record(
            conn,
            atlas_seed_id,
            atlas["عنوان"],
            f"{atlas['عنوان']}؛ نسخه {atlas.get('نسخه','')}؛ بروزرسانی {atlas.get('تاریخ_بروزرسانی','')}",
            "atlas",
            "city_atlas",
            "هرمزگان",
            "بندرعباس",
            None,
            "بندرعباس",
            atlas["موقعیت_شهر"]["مرکز_مختصات"]["lat"],
            atlas["موقعیت_شهر"]["مرکز_مختصات"]["lon"],
            atlas.get("منبع", ""),
            0.99,
            "fa",
            "bandari",
            "اطلس",
            ["اطلس", "بندرعباس", "شهرک‌ها", "محله‌ها"],
            ["اطلس شهرک‌ها و محله‌های بندرعباس", "بندرعباس", "هرمزگان"],
            ["اطلس", "بندرعباس"],
            atlas,
        )
        add_knowledge_row(
            conn,
            atlas_seed_id,
            atlas["عنوان"],
            f"{atlas['عنوان']}؛ نسخه {atlas.get('نسخه','')}؛ بروزرسانی {atlas.get('تاریخ_بروزرسانی','')}",
            "atlas",
            "city_atlas",
            "بندرعباس",
            "هرمزگان",
            atlas["موقعیت_شهر"]["مرکز_مختصات"]["lat"],
            atlas["موقعیت_شهر"]["مرکز_مختصات"]["lon"],
            ["اطلس", "بندرعباس", "شهرک‌ها", "محله‌ها"],
            ["اطلس شهرک‌ها و محله‌های بندرعباس", "بندرعباس", "هرمزگان"],
            atlas,
        )

        # city record
        city = atlas["موقعیت_شهر"]
        city_seed_id = "CITY_BANDARABBAS_001"
        upsert_seed_record(
            conn,
            city_seed_id,
            city["نام"],
            f"مرکز مختصات شهر {city['نام']} و فهرست شهرک‌های مهم.",
            "city",
            "urban_center",
            "هرمزگان",
            None,
            None,
            city["نام"],
            city["مرکز_مختصات"]["lat"],
            city["مرکز_مختصات"]["lon"],
            atlas.get("منبع", ""),
            0.98,
            "fa",
            "bandari",
            "اطلاعات_شهر",
            ["بندرعباس", "شهر", "مرکز"],
            [city["نام"]] + city.get("شهرک‌های_مهم", []),
            ["بندرعباس"],
            city,
        )
        add_knowledge_row(
            conn,
            city_seed_id,
            city["نام"],
            f"مرکز مختصات شهر {city['نام']} و فهرست شهرک‌های مهم.",
            "city",
            "urban_center",
            city["نام"],
            "هرمزگان",
            city["مرکز_مختصات"]["lat"],
            city["مرکز_مختصات"]["lon"],
            ["بندرعباس", "شهر", "مرکز"],
            [city["نام"]] + city.get("شهرک‌های_مهم", []),
            city,
        )

        for key, item in walk_items(atlas):
            title = item.get("نام") or key.replace("_", " ")
            seed_id = f"ATLAS_{slugify_fa(title)}"
            content = json.dumps(item, ensure_ascii=False)
            upsert_seed_record(
                conn,
                seed_id,
                title,
                content,
                "neighborhood",
                item.get("بافت", {}).get("نوع", "urban_area"),
                "هرمزگان",
                "بندرعباس",
                item.get("موقعیت", ""),
                "بندرعباس",
                item.get("مختصات_مرکز", {}).get("lat"),
                item.get("مختصات_مرکز", {}).get("lon"),
                atlas.get("منبع", ""),
                item.get("امتیاز_رضایت", 0.95),
                "fa",
                "bandari",
                "اطلاعات_محله",
                item.get("tags", []),
                item.get("keywords", []),
                item.get("voice_keywords", []),
                item,
            )
            add_knowledge_row(
                conn,
                seed_id,
                title,
                content,
                "neighborhood",
                item.get("بافت", {}).get("نوع", "urban_area"),
                "بندرعباس",
                "هرمزگان",
                item.get("مختصات_مرکز", {}).get("lat"),
                item.get("مختصات_مرکز", {}).get("lon"),
                item.get("tags", []),
                item.get("keywords", []),
                item,
            )

            refs = item.get("نقاط_مرجع", [])
            for idx, ref in enumerate(refs, start=1):
                ref_title = f"{title} - {ref.get('نام','نقطه مرجع')}"
                ref_seed_id = f"{seed_id}_REF_{idx:02d}"
                ref_content = f"نقطه مرجع وابسته به {title}: {json.dumps(ref, ensure_ascii=False)}"
                upsert_seed_record(
                    conn,
                    ref_seed_id,
                    ref_title,
                    ref_content,
                    "reference_point",
                    ref.get("نوع", "landmark"),
                    "هرمزگان",
                    "بندرعباس",
                    None,
                    None,
                    atlas.get("منبع", ""),
                    item.get("امتیاز_رضایت", 0.95),
                    "fa",
                    "bandari",
                    "نقطه_مرجع",
                    [title, ref.get("نام", ""), ref.get("نوع", "")],
                    [ref.get("نام", ""), title],
                    [ref.get("نام", "")],
                    ref,
                )
                add_knowledge_row(
                    conn,
                    ref_seed_id,
                    ref_title,
                    ref_content,
                    "reference_point",
                    ref.get("نوع", "landmark"),
                    "بندرعباس",
                    "هرمزگان",
                    ref.get("lat"),
                    ref.get("lon"),
                    [title, ref.get("نام", ""), ref.get("نوع", "")],
                    [ref.get("نام", ""), title],
                    ref,
                )

        # summary rows
        for i, row in enumerate(atlas.get("جدول_جمع‌بندی_و_مقایسه", []), start=1):
            title = f"مقایسه محله‌ها - شاخص {row.get('شاخص', f'{i}')}"
            seed_id = f"ATLAS_SUMMARY_{i:02d}"
            upsert_seed_record(
                conn,
                seed_id,
                title,
                json.dumps(row, ensure_ascii=False),
                "summary",
                "comparison",
                "هرمزگان",
                "بندرعباس",
                None,
                None,
                atlas.get("منبع", ""),
                0.90,
                "fa",
                "bandari",
                "مقایسه_محله",
                [row.get("شاخص", "")],
                list(row.values()),
                [],
                row,
            )
            add_knowledge_row(
                conn,
                seed_id,
                title,
                json.dumps(row, ensure_ascii=False),
                "summary",
                "comparison",
                "بندرعباس",
                "هرمزگان",
                None,
                None,
                [row.get("شاخص", "")],
                list(row.values()),
                row,
            )

        conn.commit()
        print("IMPORTED_ATLAS=1")

if __name__ == "__main__":
    import_atlas()
