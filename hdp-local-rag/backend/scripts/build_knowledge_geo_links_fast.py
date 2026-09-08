from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import sqlite3
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DB = ROOT / "hdp_v2_embedding_ok.db"
GEO_DB = ROOT / "geo.db"
STATE_FILE = ROOT / "archive" / "backups" / "knowledge_geo_populate_state.json"
BACKUP_DIR = ROOT / "archive" / "backups" / f"knowledge_geo_populate_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

GEO_TABLES = ["hospitals", "cameras", "fuel_stations", "roads", "pois", "traffic"]

TABLE_HINTS = {
    "hospitals": ["hospital", "clinic", "medical", "health", "بیمارستان", "درمانگاه", "کلینیک", "پزشک", "درمان"],
    "cameras": ["camera", "cctv", "traffic camera", "دوربین", "نظارت"],
    "fuel_stations": ["fuel", "gas", "gasoline", "cng", "diesel", "جایگاه", "پمپ", "سوخت"],
    "roads": ["road", "street", "route", "highway", "bridge", "avenue", "boulevard", "جاده", "خیابان", "بزرگراه", "پل", "مسیر"],
    "traffic": ["traffic", "accident", "blackspot", "ترافیک", "حادثه", "تصادف", "نقاط حادثه"],
    "pois": ["poi", "tourism", "tourist", "attraction", "park", "beach", "restaurant", "cafe", "hotel", "museum", "shopping", "landmark", "جاذبه", "گردشگری", "پارک", "ساحل", "رستوران", "کافه", "هتل", "موزه", "بازار"],
}

STOPWORDS = {
    "the", "and", "of", "for", "in", "on", "at", "to", "a", "an", "is", "are",
    "و", "در", "به", "از", "با", "برای", "یک", "این", "آن", "که", "را", "ها", "های",
}

def normalize(text: Any) -> str:
    if text is None:
        return ""
    s = str(text).replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^0-9a-z\u0600-\u06FF]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokens(text: Any) -> List[str]:
    s = normalize(text)
    return [t for t in s.split() if len(t) > 1 and t not in STOPWORDS]

def parse_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None

def parse_int(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        return int(v)
    except Exception:
        return None

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def backup_knowledge_db() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dst = BACKUP_DIR / KNOWLEDGE_DB.name
    shutil.copy2(KNOWLEDGE_DB, dst)
    return dst

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None

def columns(conn: sqlite3.Connection, table: str) -> List[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]

def first_existing_table(conn: sqlite3.Connection, candidates: Sequence[str]) -> Optional[str]:
    for t in candidates:
        if table_exists(conn, t):
            return t
    return None

def get_first(d: Dict[str, Any], names: Sequence[str], default: Any = None) -> Any:
    for n in names:
        if n in d and d[n] is not None:
            return d[n]
    return default

def load_aliases(conn: sqlite3.Connection) -> Dict[int, List[str]]:
    alias_map: Dict[int, List[str]] = defaultdict(list)
    for table, alias_col, id_col in [
        ("knowledge_aliases", "alias_title", "knowledge_id"),
        ("aliases", "alias", "knowledge_id"),
    ]:
        if not table_exists(conn, table):
            continue
        cols = set(columns(conn, table))
        if alias_col not in cols or id_col not in cols:
            continue
        for kid, alias in conn.execute(f"SELECT {id_col}, {alias_col} FROM {table}"):
            kid_int = parse_int(kid)
            alias_text = str(alias or "").strip()
            if kid_int is not None and alias_text:
                alias_map[kid_int].append(alias_text)
    return alias_map

def load_knowledge_items(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    table = first_existing_table(conn, ["knowledge", "atlas_master", "entities", "master_knowledge"])
    if not table:
        return []

    cols = set(columns(conn, table))
    id_col = next((c for c in ["knowledge_id", "id", "node_id", "entity_id"] if c in cols), None)
    title_col = next((c for c in ["title", "name", "atlas_name", "canonical_name", "entity", "label"] if c in cols), None)
    category_col = next((c for c in ["category", "cat", "topic", "subcategory", "type"] if c in cols), None)
    content_col = next((c for c in ["content", "description", "body", "summary", "text"] if c in cols), None)
    lat_col = next((c for c in ["lat", "latitude"] if c in cols), None)
    lng_col = next((c for c in ["lng", "lon", "longitude"] if c in cols), None)

    if not id_col or not title_col:
        return []

    alias_map = load_aliases(conn)
    out = []
    for row in conn.execute(f"SELECT * FROM {table}"):
        d = dict(row)
        kid = parse_int(get_first(d, [id_col]))
        title = str(get_first(d, [title_col], "") or "").strip()
        if kid is None or not title:
            continue
        out.append(
            {
                "knowledge_id": kid,
                "title": title,
                "category": str(get_first(d, [category_col], "") or "").strip(),
                "content": str(get_first(d, [content_col], "") or "").strip(),
                "lat": parse_float(get_first(d, [lat_col], None)) if lat_col else None,
                "lng": parse_float(get_first(d, [lng_col], None)) if lng_col else None,
                "aliases": alias_map.get(kid, []),
            }
        )
    return out

def load_geo_items(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for table in GEO_TABLES:
        if not table_exists(conn, table):
            continue

        cols = set(columns(conn, table))
        id_col = "id" if "id" in cols else None
        name_col = next((c for c in ["name", "title", "code"] if c in cols), None)
        category_col = next((c for c in ["category", "type", "road_class", "level", "status"] if c in cols), None)
        lat_col = next((c for c in ["lat", "latitude"] if c in cols), None)
        lng_col = next((c for c in ["lng", "lon", "longitude"] if c in cols), None)

        if not id_col or not name_col:
            continue

        for row in conn.execute(f"SELECT * FROM {table}"):
            d = dict(row)
            gid = parse_int(get_first(d, [id_col]))
            name = str(get_first(d, [name_col], "") or "").strip()
            if gid is None or not name:
                continue

            category = str(get_first(d, [category_col], "") or "").strip() if category_col else ""
            lat = parse_float(get_first(d, [lat_col], None)) if lat_col else None
            lng = parse_float(get_first(d, [lng_col], None)) if lng_col else None

            if table == "roads" and (lat is None or lng is None):
                min_lat = parse_float(d.get("min_lat"))
                max_lat = parse_float(d.get("max_lat"))
                min_lng = parse_float(d.get("min_lng"))
                max_lng = parse_float(d.get("max_lng"))
                if None not in (min_lat, max_lat, min_lng, max_lng):
                    lat = (min_lat + max_lat) / 2.0
                    lng = (min_lng + max_lng) / 2.0

            if table == "fuel_stations" and not category:
                parts = []
                if int(d.get("gasoline") or 0):
                    parts.append("gasoline")
                if int(d.get("cng") or 0):
                    parts.append("cng")
                if int(d.get("diesel") or 0):
                    parts.append("diesel")
                category = ",".join(parts) if parts else "fuel"

            if table == "cameras" and not category:
                category = str(d.get("types_json") or "").strip() or "camera"

            items.append(
                {
                    "geo_table": table,
                    "geo_id": gid,
                    "name": name,
                    "category": category,
                    "lat": lat,
                    "lng": lng,
                }
            )
    return items

def build_indexes(geo_items: List[Dict[str, Any]]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
    exact: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    inverted: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for item in geo_items:
        n = normalize(item["name"])
        if n:
            exact[n].append(item)
        bag = f"{item['name']} {item.get('category','')} {item['geo_table']}"
        for tok in set(tokens(bag)):
            inverted[tok].append(item)
    return exact, inverted

def hints(text: str) -> List[str]:
    s = normalize(text)
    out = []
    for table, kws in TABLE_HINTS.items():
        if any(k in s for k in kws):
            out.append(table)
    return out

def pool_for_knowledge(k: Dict[str, Any], exact, inverted, geo_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []

    def add(item: Dict[str, Any]) -> None:
        key = (item["geo_table"], item["geo_id"])
        if key in seen:
            return
        seen.add(key)
        out.append(item)

    for item in exact.get(normalize(k["title"]), []):
        add(item)

    for alias in k.get("aliases", []):
        for item in exact.get(normalize(alias), []):
            add(item)

    search_text = " ".join([k["title"], k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])
    for tok in tokens(search_text):
        for item in inverted.get(tok, []):
            add(item)

    for table in hints(search_text):
        for item in geo_items:
            if item["geo_table"] == table:
                add(item)

    if not out:
        for item in geo_items[:200]:
            add(item)

    return out[:400]

def score(k: Dict[str, Any], g: Dict[str, Any]) -> Tuple[float, str]:
    kt = normalize(k["title"])
    gt = normalize(g["name"])

    if kt and kt == gt:
        return 1.0, "exact_name"

    for alias in k.get("aliases", []):
        if normalize(alias) == gt:
            return 0.99, "alias_match"

    ratio = max(
        SequenceMatcher(None, kt, gt).ratio(),
        max((SequenceMatcher(None, normalize(a), gt).ratio() for a in k.get("aliases", [])), default=0.0),
    )

    tk = set(tokens(" ".join([k["title"], k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])))
    tg = set(tokens(" ".join([g["name"], g.get("category", ""), g["geo_table"]])))
    overlap = len(tk & tg)
    token_bonus = min(0.18, overlap * 0.04)

    category_bonus = 0.12 if g["geo_table"] in hints(" ".join([k["title"], k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])) else 0.0

    geo_bonus = 0.0
    klat, klng = k.get("lat"), k.get("lng")
    glat, glng = g.get("lat"), g.get("lng")
    if klat is not None and klng is not None and glat is not None and glng is not None:
        dist = haversine_km(klat, klng, glat, glng)
        if dist <= 10:
            geo_bonus = max(0.0, 0.20 * (1.0 - dist / 10.0))

    final = min(1.0, (ratio * 0.74) + token_bonus + category_bonus + geo_bonus)
    kind = "strong_match" if final >= 0.92 else ("category_geo_match" if (category_bonus > 0 or geo_bonus > 0) else "fuzzy_match")
    return final, kind

def init_knowledge_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_geo_link (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        knowledge_id INTEGER NOT NULL,
        geo_table TEXT NOT NULL,
        geo_id INTEGER NOT NULL,
        relation_type TEXT DEFAULT 'related',
        confidence REAL DEFAULT 1.0,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )
    """)
    conn.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_geo_link
    ON knowledge_geo_link(knowledge_id, geo_table, geo_id)
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_kgl_knowledge
    ON knowledge_geo_link(knowledge_id)
    """)
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_kgl_geo
    ON knowledge_geo_link(geo_table, geo_id)
    """)

def get_resume_state() -> int:
    if not STATE_FILE.exists():
        return 0
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return int(data.get("offset", 0))
    except Exception:
        return 0

def save_resume_state(offset: int) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"offset": offset, "updated_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False, indent=2), encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-score", type=float, default=0.88)
    parser.add_argument("--max-links", type=int, default=3)
    parser.add_argument("--knowledge-batch", type=int, default=250)
    parser.add_argument("--geo-limit", type=int, default=0)
    args = parser.parse_args()

    if not KNOWLEDGE_DB.exists():
        raise FileNotFoundError(KNOWLEDGE_DB)
    if not GEO_DB.exists():
        raise FileNotFoundError(GEO_DB)

    backup_path = backup_knowledge_db()
    print(f"BACKUP {backup_path}")

    with sqlite3.connect(str(KNOWLEDGE_DB)) as kconn, sqlite3.connect(str(GEO_DB)) as gconn:
        kconn.row_factory = sqlite3.Row
        gconn.row_factory = sqlite3.Row

        init_knowledge_db(kconn)

        all_knowledge = load_knowledge_items(kconn)
        if not all_knowledge:
            print("SCANNED=0")
            print("INSERTED=0")
            return

        geo_items = load_geo_items(gconn)
        if args.geo_limit and args.geo_limit > 0:
            geo_items = geo_items[:args.geo_limit]

        exact, inverted = build_indexes(geo_items)

        resume_offset = get_resume_state()
        total_scanned = 0
        total_inserted = 0
        now_ts = int(datetime.now(timezone.utc).timestamp())

        insert_sql = """
        INSERT OR IGNORE INTO knowledge_geo_link
        (knowledge_id, geo_table, geo_id, relation_type, confidence, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        for start in range(resume_offset, len(all_knowledge), args.knowledge_batch):
            batch = all_knowledge[start:start + args.knowledge_batch]
            batch_rows: List[Tuple[int, str, int, str, float, int]] = []

            for k in batch:
                total_scanned += 1
                pool = pool_for_knowledge(k, exact, inverted, geo_items)
                candidates: List[Tuple[float, str, Dict[str, Any]]] = []

                for g in pool:
                    s, kind = score(k, g)
                    if s >= args.min_score:
                        candidates.append((s, kind, g))

                if not candidates:
                    continue

                candidates.sort(key=lambda x: (x[0], x[2]["geo_table"], x[2]["geo_id"]), reverse=True)
                for s, kind, g in candidates[:args.max_links]:
                    batch_rows.append(
                        (
                            k["knowledge_id"],
                            g["geo_table"],
                            g["geo_id"],
                            kind,
                            float(round(s, 4)),
                            now_ts,
                        )
                    )

            if batch_rows:
                kconn.executemany(insert_sql, batch_rows)
                kconn.commit()
                total_inserted += len(batch_rows)

            save_resume_state(start + len(batch))
            print(f"BATCH_DONE offset={start + len(batch)} scanned={total_scanned} inserted={total_inserted}")

        print(f"SCANNED={total_scanned}")
        print(f"INSERTED={total_inserted}")

if __name__ == "__main__":
    main()
