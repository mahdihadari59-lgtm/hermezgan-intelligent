from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
DB_DEFAULT = ROOT / "hdp_v2_embedding_ok.db"

SKIP_KEYS = {
    "موقعیت_شهر",
    "جدول_جمع‌بندی_و_مقایسه",
    "نقاط_مرجع_عمومی_منطقه",
    "منابع",
    "source",
    "source_file",
    "file",
    "meta",
    "metadata",
}

def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    s = str(value).replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip()
    s = re.sub(r"[^0-9a-z\u0600-\u06FF]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v

def as_text(v: Any) -> Optional[str]:
    v = scalar(v)
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    t = str(v).strip()
    return t if t else None

def as_float(v: Any) -> Optional[float]:
    v = scalar(v)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None

def as_list(v: Any) -> List[str]:
    v = scalar(v)
    if v is None:
        return []
    if isinstance(v, list):
        out: List[str] = []
        for item in v:
            t = as_text(item)
            if t:
                out.append(t)
        return out
    if isinstance(v, str):
        parts = [p.strip() for p in re.split(r"[|,؛/]+", v) if p.strip()]
        return parts
    t = as_text(v)
    return [t] if t else []

def safe_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

def backup_db(db_path: Path) -> Path:
    backup_dir = ROOT / "archive" / "backups" / f"bundle_import_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    dst = backup_dir / db_path.name
    shutil.copy2(db_path, dst)
    return dst

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None

def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]

def ensure_seed_table(conn: sqlite3.Connection) -> None:
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

def ensure_knowledge_table(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        keywords TEXT,
        source TEXT,
        priority INTEGER DEFAULT 1,
        subcategory TEXT,
        question TEXT,
        answer TEXT,
        city TEXT,
        lat REAL,
        lon REAL,
        updated_at DATETIME,
        category_fa TEXT,
        valid_until DATE,
        tags TEXT,
        topic TEXT,
        status TEXT DEFAULT 'active',
        subtopic TEXT,
        atlas TEXT,
        intent TEXT,
        main_intent TEXT,
        sub_intent TEXT,
        expert_name TEXT,
        is_deleted INTEGER DEFAULT 0,
        verified INTEGER DEFAULT 0,
        last_verified TEXT,
        confidence REAL,
        merged_into INTEGER,
        quality TEXT,
        entity_type TEXT,
        parent_id INTEGER,
        relation_type TEXT,
        graph_parent INTEGER,
        graph_depth INTEGER DEFAULT 0,
        graph_root TEXT,
        graph_path TEXT
    )
    """)

def rec_title(rec: Dict[str, Any], fallback: str) -> str:
    return as_text(
        rec.get("title")
        or rec.get("عنوان")
        or rec.get("name")
        or rec.get("نام")
        or rec.get("label")
        or fallback
    ) or fallback

def rec_content(rec: Dict[str, Any], title: str) -> str:
    content = rec.get("content") or rec.get("description") or rec.get("body") or rec.get("summary") or rec.get("متن")
    if content is not None:
        text = as_text(content)
        if text:
            return text

    parts = []
    for k in ("موقعیت", "بافت", "کاربری", "دسترسی‌ها", "مراکز_نزدیک", "امکانات_رفاهی", "مزیت_رقابتی", "وضعیت_ترافیکی", "نکته_ویژه", "هشدار_ترافیکی", "امتیاز_رضایت"):
        if k in rec and rec[k] is not None:
            parts.append(f"{k}: {safe_json(rec[k])}")
    if parts:
        return f"{title} | " + " | ".join(parts)

    return safe_json(rec)

def extract_common(rec: Dict[str, Any], source_file: str, fallback_category: str = "") -> Dict[str, Any]:
    title = rec_title(rec, Path(source_file).stem)
    content = rec_content(rec, title)
    category = as_text(rec.get("category") or rec.get("category_fa") or rec.get("cat") or rec.get("موضوع") or fallback_category) or fallback_category
    subcategory = as_text(rec.get("subcategory") or rec.get("sub_category") or rec.get("subcategory_fa") or rec.get("زیر_دسته") or rec.get("زیرگروه"))
    city = as_text(rec.get("city") or rec.get("شهر") or "بندرعباس")
    province = as_text(rec.get("province") or rec.get("استان") or "هرمزگان")
    county = as_text(rec.get("county") or rec.get("شهرستان"))
    district = as_text(rec.get("district") or rec.get("منطقه"))
    lat = as_float(rec.get("latitude") or rec.get("lat"))
    lon = as_float(rec.get("longitude") or rec.get("lon") or rec.get("lng"))
    source = as_text(rec.get("source") or rec.get("منبع") or source_file) or source_file
    confidence = as_float(rec.get("confidence")) or 0.80
    language = as_text(rec.get("language") or "fa") or "fa"
    dialect = as_text(rec.get("dialect") or "bandari")
    intent = as_text(rec.get("intent") or rec.get("main_intent") or rec.get("sub_intent"))
    tags = as_list(rec.get("tags"))
    keywords = as_list(rec.get("keywords")) + as_list(rec.get("voice_keywords"))
    return {
        "title": title,
        "content": content,
        "category": category,
        "subcategory": subcategory,
        "city": city,
        "province": province,
        "county": county,
        "district": district,
        "lat": lat,
        "lon": lon,
        "source": source,
        "confidence": confidence,
        "language": language,
        "dialect": dialect,
        "intent": intent,
        "tags": tags,
        "keywords": keywords,
        "raw": rec,
    }

def looks_like_record(obj: Dict[str, Any]) -> bool:
    has_title = any(k in obj for k in ("title", "عنوان", "name", "نام", "label"))
    has_content = any(k in obj for k in ("content", "description", "body", "summary", "متن"))
    return has_title and (has_content or len(obj) > 3)

def expand_bundle(obj: Dict[str, Any], source_file: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    if looks_like_record(obj):
        records.append(extract_common(obj, source_file, Path(source_file).stem))
        return records

    # Special atlas-like layout
    atlas_title = as_text(obj.get("عنوان") or obj.get("title") or obj.get("name") or Path(source_file).stem) or Path(source_file).stem
    city_meta = obj.get("موقعیت_شهر") if isinstance(obj.get("موقعیت_شهر"), dict) else {}

    if city_meta:
        city_rec = {
            "title": as_text(city_meta.get("نام") or atlas_title) or atlas_title,
            "content": f"اطلس شهری {atlas_title} | {safe_json(city_meta)}",
            "category": "city",
            "subcategory": "urban_center",
            "city": city_meta.get("نام") or "بندرعباس",
            "province": "هرمزگان",
            "lat": city_meta.get("مرکز_مختصات", {}).get("lat") if isinstance(city_meta.get("مرکز_مختصات"), dict) else None,
            "lon": city_meta.get("مرکز_مختصات", {}).get("lon") if isinstance(city_meta.get("مرکز_مختصات"), dict) else None,
            "source": obj.get("منبع") or source_file,
            "confidence": 0.98,
            "language": "fa",
            "dialect": "bandari",
            "intent": "اطلاعات_شهر",
            "tags": ["اطلس", "شهر"],
            "keywords": [atlas_title, city_meta.get("نام") or "بندرعباس"],
        }
        records.append(extract_common(city_rec, source_file, "city"))

    for key, value in obj.items():
        if key in SKIP_KEYS:
            continue

        if isinstance(value, dict) and (key.startswith("محله_") or key.startswith("شهرک_")):
            title = as_text(value.get("نام") or key.replace("_", " ")) or key.replace("_", " ")
            content = f"{title} | {safe_json(value)}"
            rec = {
                "title": title,
                "content": content,
                "category": "neighborhood",
                "subcategory": as_text(value.get("بافت", {}).get("نوع") if isinstance(value.get("بافت"), dict) else None) or "urban_area",
                "city": "بندرعباس",
                "province": "هرمزگان",
                "lat": value.get("مختصات_مرکز", {}).get("lat") if isinstance(value.get("مختصات_مرکز"), dict) else None,
                "lon": value.get("مختصات_مرکز", {}).get("lon") if isinstance(value.get("مختصات_مرکز"), dict) else None,
                "source": obj.get("منبع") or source_file,
                "confidence": as_float(value.get("امتیاز_رضایت")) or 0.90,
                "language": "fa",
                "dialect": "bandari",
                "intent": "اطلاعات_محله",
                "tags": ["محله", "شهرک", "بندرعباس"],
                "keywords": [title, atlas_title],
                "voice_keywords": [title],
                "raw": value,
            }
            records.append(extract_common(rec, source_file, "neighborhood"))
            for ref in value.get("نقاط_مرجع", []) if isinstance(value.get("نقاط_مرجع"), list) else []:
                if not isinstance(ref, dict):
                    continue
                ref_title = f"{title} - {as_text(ref.get('نام') or 'نقطه مرجع')}"
                ref_rec = {
                    "title": ref_title,
                    "content": f"نقطه مرجع وابسته به {title} | {safe_json(ref)}",
                    "category": "reference_point",
                    "subcategory": as_text(ref.get("نوع") or "landmark"),
                    "city": "بندرعباس",
                    "province": "هرمزگان",
                    "lat": ref.get("lat"),
                    "lon": ref.get("lon"),
                    "source": obj.get("منبع") or source_file,
                    "confidence": 0.88,
                    "language": "fa",
                    "dialect": "bandari",
                    "intent": "نقطه_مرجع",
                    "tags": [title, as_text(ref.get("نوع") or "") or ""],
                    "keywords": [ref_title, title],
                    "voice_keywords": [ref_title],
                    "raw": ref,
                }
                records.append(extract_common(ref_rec, source_file, "reference_point"))

        elif isinstance(value, list) and key == "نقاط_مرجع_عمومی_منطقه":
            for ref in value:
                if not isinstance(ref, dict):
                    continue
                title = as_text(ref.get("نام") or "نقطه مرجع")
                rec = {
                    "title": title,
                    "content": f"نقطه مرجع عمومی | {safe_json(ref)}",
                    "category": as_text(ref.get("نوع") or "reference_point"),
                    "subcategory": "reference_point",
                    "city": "بندرعباس",
                    "province": "هرمزگان",
                    "lat": ref.get("lat"),
                    "lon": ref.get("lon"),
                    "source": obj.get("منبع") or source_file,
                    "confidence": 0.88,
                    "language": "fa",
                    "dialect": "bandari",
                    "intent": "نقطه_مرجع",
                    "tags": [as_text(ref.get("نوع") or "") or ""],
                    "keywords": [title],
                    "voice_keywords": [title],
                    "raw": ref,
                }
                records.append(extract_common(rec, source_file, "reference_point"))

        elif isinstance(value, list) and key == "جدول_جمع‌بندی_و_مقایسه":
            for i, row in enumerate(value, start=1):
                if not isinstance(row, dict):
                    continue
                title = f"مقایسه محله‌ها - {as_text(row.get('شاخص') or i)}"
                rec = {
                    "title": title,
                    "content": f"جدول مقایسه | {safe_json(row)}",
                    "category": "summary",
                    "subcategory": "comparison",
                    "city": "بندرعباس",
                    "province": "هرمزگان",
                    "source": obj.get("منبع") or source_file,
                    "confidence": 0.85,
                    "language": "fa",
                    "dialect": "bandari",
                    "intent": "مقایسه_محله",
                    "tags": [as_text(row.get('شاخص') or "مقایسه") or "مقایسه"],
                    "keywords": list(row.values()) if isinstance(row, dict) else [title],
                    "voice_keywords": [title],
                    "raw": row,
                }
                records.append(extract_common(rec, source_file, "summary"))

    if records:
        return records

    # Generic fallback: recursively find dict items that look like records.
    for key, value in obj.items():
        if isinstance(value, dict) and looks_like_record(value):
            child = dict(value)
            child.setdefault("title", value.get("title") or value.get("عنوان") or key)
            records.append(extract_common(child, source_file, "knowledge"))
        elif isinstance(value, list):
            for idx, item in enumerate(value, start=1):
                if isinstance(item, dict) and looks_like_record(item):
                    child = dict(item)
                    child.setdefault("title", item.get("title") or item.get("عنوان") or f"{key}-{idx}")
                    records.append(extract_common(child, source_file, "knowledge"))

    return records

def load_json_files(source_dir: Path) -> List[Tuple[Path, Any]]:
    files = sorted([p for p in source_dir.rglob("hormozgan*.json") if p.is_file()])
    out: List[Tuple[Path, Any]] = []

    for fp in files:
        try:
            if fp.stat().st_size == 0:
                print(f"SKIP_EMPTY {fp.name}")
                continue

            raw = fp.read_text(encoding="utf-8-sig").strip()
            if not raw:
                print(f"SKIP_EMPTY {fp.name}")
                continue

            data = json.loads(raw)
            out.append((fp, data))
        except Exception as e:
            print(f"SKIP_FILE {fp.name} :: {e}")

    return out

def dedup_key(rec: Dict[str, Any]) -> str:
    return "|".join([
        normalize_text(rec.get("title")),
        normalize_text(rec.get("city")),
        normalize_text(rec.get("category")),
        normalize_text(rec.get("subcategory")),
    ])

def build_knowledge_row(conn: sqlite3.Connection, rec: Dict[str, Any], columns: set[str]) -> int:
    title = as_text(rec.get("title")) or "بدون عنوان"
    content = as_text(rec.get("content")) or title
    category = as_text(rec.get("category"))
    subcategory = as_text(rec.get("subcategory"))
    city = as_text(rec.get("city"))
    lat = rec.get("lat")
    lon = rec.get("lon")
    source = as_text(rec.get("source"))
    confidence = rec.get("confidence")
    tags = rec.get("tags") or []
    keywords = rec.get("keywords") or []
    intent = as_text(rec.get("intent"))
    atlas = as_text(rec.get("atlas")) or source
    category_fa = category
    subtopic = subcategory or category
    main_intent = intent
    sub_intent = None
    expert_name = None
    topic = category or subcategory or "general"

    row = conn.execute(
        "SELECT id FROM knowledge WHERE title=? AND IFNULL(city,'')=? AND IFNULL(subcategory,'')=? LIMIT 1",
        (title, city or "", subcategory or ""),
    ).fetchone()

    now = datetime.now(timezone.utc).isoformat()

    field_map = {
        "title": title,
        "category": category,
        "content": content,
        "keywords": ", ".join([x for x in as_list(keywords) if x]),
        "source": source,
        "priority": 1,
        "subcategory": subcategory,
        "question": None,
        "answer": None,
        "city": city,
        "lat": lat,
        "lon": lon,
        "updated_at": now,
        "category_fa": category_fa,
        "valid_until": None,
        "tags": ", ".join([x for x in as_list(tags) if x]),
        "topic": topic,
        "status": "active",
        "subtopic": subtopic,
        "atlas": atlas,
        "intent": intent,
        "main_intent": main_intent,
        "sub_intent": sub_intent,
        "expert_name": expert_name,
        "is_deleted": 0,
        "verified": 1 if confidence and float(confidence) >= 0.85 else 0,
        "last_verified": now if confidence and float(confidence) >= 0.85 else None,
        "confidence": confidence,
        "merged_into": None,
        "quality": "high" if confidence and float(confidence) >= 0.9 else "normal",
        "entity_type": "atlas" if topic == "atlas" else "location",
        "parent_id": None,
        "relation_type": None,
        "graph_parent": None,
        "graph_depth": 0,
        "graph_root": title,
        "graph_path": title,
    }

    if row:
        kid = int(row[0])
        sets = []
        vals = []
        for col, val in field_map.items():
            if col in columns:
                sets.append(f"{col}=?")
                vals.append(val)
        if sets:
            conn.execute(f"UPDATE knowledge SET {', '.join(sets)} WHERE id=?", (*vals, kid))
        return kid

    insert_cols = [c for c in field_map.keys() if c in columns]
    insert_vals = [field_map[c] for c in insert_cols]
    placeholders = ", ".join(["?"] * len(insert_cols))
    conn.execute(
        f"INSERT INTO knowledge ({', '.join(insert_cols)}) VALUES ({placeholders})",
        tuple(insert_vals),
    )
    return int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])

def upsert_seed(conn: sqlite3.Connection, rec: Dict[str, Any], source_file: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    seed_id = normalize_text(rec.get("title") or "") or f"{Path(source_file).stem}_{abs(hash(safe_json(rec))) % 10_000_000}"
    conn.execute(
        """
        INSERT INTO knowledge_seed_records (
            seed_id, title, content, category, subcategory, province, county, district, city,
            latitude, longitude, source, confidence, language, dialect, intent,
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
            as_text(rec.get("title")),
            as_text(rec.get("content")),
            as_text(rec.get("category")),
            as_text(rec.get("subcategory")),
            as_text(rec.get("province")),
            as_text(rec.get("county")),
            as_text(rec.get("district")),
            as_text(rec.get("city")),
            rec.get("lat"),
            rec.get("lon"),
            as_text(rec.get("source")) or source_file,
            rec.get("confidence"),
            as_text(rec.get("language")) or "fa",
            as_text(rec.get("dialect")) or "bandari",
            as_text(rec.get("intent")),
            safe_json(rec.get("tags") or []),
            safe_json(rec.get("keywords") or []),
            safe_json(rec.get("voice_keywords") or []),
            safe_json(rec.get("raw") or rec),
            now,
            now,
        ),
    )

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default=str(Path.cwd()), help="Folder containing JSON files")
    parser.add_argument("--db", type=str, default=str(DB_DEFAULT), help="SQLite database path")
    parser.add_argument("--limit", type=int, default=0, help="Limit imported records")
    args = parser.parse_args()

    source_dir = Path(args.source).expanduser().resolve()
    db_path = Path(args.db).expanduser().resolve()

    if not source_dir.exists():
        raise FileNotFoundError(source_dir)
    if not db_path.exists():
        raise FileNotFoundError(db_path)

    backup = backup_db(db_path)
    print(f"BACKUP {backup}")

    files = load_json_files(source_dir)
    if not files:
        print("NO_JSON_FILES")
        return

    seen = set()
    selected: List[Tuple[str, Dict[str, Any]]] = []

    for fp, data in files:
        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict):
            candidates = expand_bundle(data, fp.name)
            if not candidates and looks_like_record(data):
                candidates = [extract_common(data, fp.name, fp.stem)]
        else:
            candidates = []

        for rec in candidates:
            if not isinstance(rec, dict):
                continue
            title = as_text(rec.get("title"))
            content = as_text(rec.get("content"))
            if not title:
                continue
            if not content:
                continue
            if len(normalize_text(content)) < 8:
                continue

            key = dedup_key(rec)
            if key in seen:
                continue
            seen.add(key)
            rec["source_file"] = fp.name
            selected.append((fp.name, rec))

    if args.limit and args.limit > 0:
        selected = selected[:args.limit]

    with sqlite3.connect(str(db_path)) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")

        ensure_seed_table(conn)
        ensure_knowledge_table(conn)

        cols = set(table_columns(conn, "knowledge"))

        imported = 0
        updated = 0

        for source_file, rec in selected:
            upsert_seed(conn, rec, source_file)
            kid = build_knowledge_row(conn, rec, cols)
            if kid:
                imported += 1
            else:
                updated += 1

        conn.commit()

    print(f"FILES={len(files)}")
    print(f"SELECTED={len(selected)}")
    print(f"IMPORTED={imported}")
    print(f"UPDATED={updated}")

if __name__ == "__main__":
    main()
