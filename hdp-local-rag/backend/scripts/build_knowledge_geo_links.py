from __future__ import annotations

import argparse
import math
import re
import shutil
import sqlite3
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DB = ROOT / "hdp_v2_embedding_ok.db"
GEO_DB = ROOT / "geo.db"
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

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None

def columns(conn: sqlite3.Connection, table: str) -> List[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]

def get_first(d: Dict[str, Any], names: Sequence[str], default: Any = None) -> Any:
    for name in names:
        if name in d and d[name] is not None:
            return d[name]
    return default

def normalize(text: Any) -> str:
    if text is None:
        return ""
    s = str(text)
    s = s.replace("ي", "ی").replace("ك", "ک").replace("\u200c", " ")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^0-9a-z\u0600-\u06FF]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def split_tokens(text: Any) -> List[str]:
    s = normalize(text)
    if not s:
        return []
    return [t for t in s.split() if len(t) > 1 and t not in STOPWORDS]

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

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

def backup_knowledge_db() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / KNOWLEDGE_DB.name
    shutil.copy2(KNOWLEDGE_DB, backup_path)
    return backup_path

def load_aliases(conn: sqlite3.Connection) -> Dict[int, List[str]]:
    alias_map: Dict[int, List[str]] = defaultdict(list)
    for table, alias_col, id_col in [
        ("knowledge_aliases", "alias_title", "knowledge_id"),
        ("aliases", "alias", "knowledge_id"),
    ]:
        if not table_exists(conn, table):
            continue
        cols = columns(conn, table)
        if alias_col not in cols or id_col not in cols:
            continue
        for kid, alias in conn.execute(f"SELECT {id_col}, {alias_col} FROM {table}"):
            kid_int = parse_int(kid)
            if kid_int is None:
                continue
            alias_text = str(alias or "").strip()
            if alias_text:
                alias_map[kid_int].append(alias_text)
    return alias_map

def first_existing_table(conn: sqlite3.Connection, candidates: Sequence[str]) -> Optional[str]:
    for table in candidates:
        if table_exists(conn, table):
            return table
    return None

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
    rows = []
    for row in conn.execute(f"SELECT * FROM {table}"):
        d = dict(row)
        kid = parse_int(get_first(d, [id_col]))
        title = str(get_first(d, [title_col], "") or "").strip()
        if kid is None or not title:
            continue
        category = str(get_first(d, [category_col], "") or "").strip()
        content = str(get_first(d, [content_col], "") or "").strip()
        lat = parse_float(get_first(d, [lat_col], None)) if lat_col else None
        lng = parse_float(get_first(d, [lng_col], None)) if lng_col else None
        aliases = alias_map.get(kid, [])
        rows.append({
            "knowledge_id": kid,
            "title": title,
            "category": category,
            "content": content,
            "lat": lat,
            "lng": lng,
            "aliases": aliases,
            "source_table": table,
        })
    return rows

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
                fuels = []
                if int(d.get("gasoline") or 0):
                    fuels.append("gasoline")
                if int(d.get("cng") or 0):
                    fuels.append("cng")
                if int(d.get("diesel") or 0):
                    fuels.append("diesel")
                category = ",".join(fuels) if fuels else "fuel"

            if table == "cameras" and not category:
                types_json = str(d.get("types_json") or "").strip()
                category = types_json or "camera"

            items.append({
                "geo_table": table,
                "geo_id": gid,
                "name": name,
                "category": category,
                "lat": lat,
                "lng": lng,
                "raw": d,
            })
    return items

def table_hints_from_text(text: str) -> List[str]:
    s = normalize(text)
    hints = []
    for table, keys in TABLE_HINTS.items():
        if any(k in s for k in keys):
            hints.append(table)
    return hints

def build_geo_indexes(geo_items: List[Dict[str, Any]]) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
    exact_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    token_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for item in geo_items:
        name_norm = normalize(item["name"])
        if name_norm:
            exact_map[name_norm].append(item)

        token_source = f"{item['name']} {item.get('category', '')} {item['geo_table']}"
        for tok in set(split_tokens(token_source)):
            token_map[tok].append(item)

    return exact_map, token_map

def candidate_pool_for_knowledge(k: Dict[str, Any], exact_map, token_map, geo_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    pool: List[Dict[str, Any]] = []
    seen = set()

    def add(item: Dict[str, Any]) -> None:
        key = (item["geo_table"], item["geo_id"])
        if key in seen:
            return
        seen.add(key)
        pool.append(item)

    title_norm = normalize(k["title"])
    for item in exact_map.get(title_norm, []):
        add(item)

    for alias in k.get("aliases", []):
        for item in exact_map.get(normalize(alias), []):
            add(item)

    search_text = " ".join([k.get("title", ""), k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])
    for tok in split_tokens(search_text):
        for item in token_map.get(tok, []):
            add(item)

    for table in table_hints_from_text(search_text):
        for item in geo_items:
            if item["geo_table"] == table:
                add(item)

    if not pool:
        for item in geo_items:
            add(item)

    return pool[:500]

def score_match(k: Dict[str, Any], g: Dict[str, Any]) -> Tuple[float, str]:
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

    token_k = set(split_tokens(" ".join([k["title"], k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])))
    token_g = set(split_tokens(" ".join([g["name"], g.get("category", ""), g["geo_table"]])))
    overlap = len(token_k & token_g)
    token_bonus = min(0.18, overlap * 0.04)

    text = " ".join([k["title"], k.get("category", ""), k.get("content", ""), " ".join(k.get("aliases", []))])
    hints = table_hints_from_text(text)
    category_bonus = 0.12 if g["geo_table"] in hints else 0.0

    geo_bonus = 0.0
    klat, klng = k.get("lat"), k.get("lng")
    glat, glng = g.get("lat"), g.get("lng")
    if klat is not None and klng is not None and glat is not None and glng is not None:
        dist = haversine_km(klat, klng, glat, glng)
        if dist <= 10:
            geo_bonus = max(0.0, 0.20 * (1.0 - (dist / 10.0)))

    final_score = min(1.0, (ratio * 0.74) + token_bonus + category_bonus + geo_bonus)
    if final_score >= 0.92:
        kind = "strong_match"
    elif category_bonus > 0 or geo_bonus > 0:
        kind = "category_geo_match"
    else:
        kind = "fuzzy_match"
    return final_score, kind

def ensure_unique_index(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_knowledge_geo_link "
        "ON knowledge_geo_link(knowledge_id, geo_table, geo_id)"
    )

def populate(min_score: float, max_links: int) -> Tuple[int, int]:
    if not KNOWLEDGE_DB.exists():
        raise FileNotFoundError(f"Knowledge DB not found: {KNOWLEDGE_DB}")
    if not GEO_DB.exists():
        raise FileNotFoundError(f"Geo DB not found: {GEO_DB}")

    backup_path = backup_knowledge_db()
    print(f"BACKUP {backup_path}")

    inserted = 0
    scanned = 0

    with sqlite3.connect(str(KNOWLEDGE_DB)) as kconn, sqlite3.connect(str(GEO_DB)) as gconn:
        kconn.row_factory = sqlite3.Row
        gconn.row_factory = sqlite3.Row

        ensure_unique_index(kconn)

        knowledge_items = load_knowledge_items(kconn)
        geo_items = load_geo_items(gconn)
        exact_map, token_map = build_geo_indexes(geo_items)

        insert_sql = """
        INSERT OR IGNORE INTO knowledge_geo_link
        (knowledge_id, geo_table, geo_id, relation_type, confidence, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        now_ts = int(datetime.now(timezone.utc).timestamp())

        for k in knowledge_items:
            scanned += 1
            pool = candidate_pool_for_knowledge(k, exact_map, token_map, geo_items)
            scored: List[Tuple[float, str, Dict[str, Any]]] = []

            for g in pool:
                score, kind = score_match(k, g)
                if score >= min_score:
                    scored.append((score, kind, g))

            if not scored:
                continue

            scored.sort(key=lambda x: (x[0], x[2]["geo_table"], x[2]["geo_id"]), reverse=True)
            chosen = scored[:max_links]

            for score, kind, g in chosen:
                kconn.execute(
                    insert_sql,
                    (
                        k["knowledge_id"],
                        g["geo_table"],
                        g["geo_id"],
                        kind,
                        float(round(score, 4)),
                        now_ts,
                    ),
                )
                inserted += 1

        kconn.commit()

    return scanned, inserted

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-score", type=float, default=0.88)
    parser.add_argument("--max-links", type=int, default=3)
    args = parser.parse_args()

    scanned, inserted = populate(args.min_score, args.max_links)
    print(f"SCANNED={scanned}")
    print(f"INSERTED={inserted}")

if __name__ == "__main__":
    main()
