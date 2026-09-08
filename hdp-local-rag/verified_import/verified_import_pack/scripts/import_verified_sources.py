#!/usr/bin/env python3
import argparse, hashlib, json, os, re, shutil, sqlite3, sys
from datetime import datetime
from pathlib import Path


def norm(s):
    if s is None:
        return ''
    s = str(s).strip().lower()
    s = s.replace('\u200c', ' ').replace('\u200f', ' ').replace('\u200e', ' ')
    s = s.replace('ي', 'ی').replace('ى', 'ی').replace('ك', 'ک').replace('ۀ', 'ه').replace('ة', 'ه')
    s = re.sub(r'[!?؟،,؛;:.()\[\]{}"\'`*_\-–—/\\]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def table_exists(conn, name):
    row = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
    return row is not None


def require_schema(conn):
    required = ['knowledge', 'graph_nodes', 'graph_edges', 'atlas_master', 'atlas_categories', 'neighborhoods', 'roads', 'places']
    missing = [x for x in required if not table_exists(conn, x)]
    if missing:
        raise RuntimeError('Missing required tables: ' + ', '.join(missing))


def insert_ignore(conn, sql, params):
    conn.execute(sql, params)


def get_knowledge_index(conn):
    rows = conn.execute("SELECT id, title FROM knowledge WHERE title IS NOT NULL").fetchall()
    idx = {}
    for rid, title in rows:
        n = norm(title)
        if n and n not in idx:
            idx[n] = int(rid)
    return idx


def edge_insert(conn, seen, source_id, target_id, relation, confidence=1.0, weight=1.0):
    if source_id is None or target_id is None or source_id == target_id:
        return 0
    key = (int(source_id), int(target_id), relation)
    if key in seen:
        return 0
    seen.add(key)
    conn.execute(
        "INSERT INTO graph_edges(source_id,target_id,relation_type,weight,confidence) VALUES(?,?,?,?,?)",
        (source_id, target_id, relation, weight, confidence),
    )
    return 1


def deterministic_place_id(prefix, name):
    return f"{prefix}:{hashlib.sha1(norm(name).encode('utf-8')).hexdigest()[:16]}"


def main():
    ap = argparse.ArgumentParser(description='Import the three verified HDP JSON sources without recreating the polluted full-mesh graph.')
    ap.add_argument('db')
    ap.add_argument('v3')
    ap.add_argument('v2')
    ap.add_argument('knowledge_index')
    args = ap.parse_args()

    for p in (args.db, args.v3, args.v2, args.knowledge_index):
        if not Path(p).is_file():
            raise SystemExit(f'File not found: {p}')

    v3 = load_json(args.v3)
    v2 = load_json(args.v2)
    kidx = load_json(args.knowledge_index)

    if v3.get('schema_version') != '3.0.0':
        raise SystemExit(f"Unexpected v3 schema_version: {v3.get('schema_version')}")
    if not isinstance(v2.get('neighborhoods'), list) or not isinstance(v3.get('neighborhoods'), list):
        raise SystemExit('Neighborhood data missing from atlas sources')
    if not isinstance(kidx, dict):
        raise SystemExit('knowledge_index_2.json must contain a JSON object')

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    try:
        require_schema(conn)
        before_edges = conn.execute('SELECT COUNT(*) FROM graph_edges').fetchone()[0]
        if before_edges != 0:
            raise RuntimeError(f'ABORT: graph_edges is not empty ({before_edges}). This importer refuses to overwrite an existing graph.')

        before_links = conn.execute('SELECT COUNT(*) FROM knowledge_links').fetchone()[0] if table_exists(conn, 'knowledge_links') else None
        backup = f"{args.db}.before_verified_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(args.db, backup)

        knowledge_idx = get_knowledge_index(conn)
        seen_edges = set()
        stats = {
            'neighborhoods': 0,
            'roads': 0,
            'places': 0,
            'atlas_master': 0,
            'atlas_categories': 0,
            'edges': 0,
            'edge_candidates_missing_nodes': 0,
        }

        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('BEGIN IMMEDIATE')

        # Preserve all three source documents verbatim in atlas_master.
        source_docs = [
            ('bandarabbas_atlas_v3_roads_traffic_ports.json', 'verified_v3', v3),
            ('bandarabbas_deep_research_atlas_v2.json', 'verified_v2', v2),
            ('knowledge_index_2.json', 'verified_knowledge_index', kidx),
        ]
        for fname, cat, doc in source_docs:
            payload = json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            exists = conn.execute("SELECT id FROM atlas_master WHERE atlas_name=? AND category=?", (fname, cat)).fetchone()
            if exists:
                conn.execute("UPDATE atlas_master SET content=? WHERE id=?", (payload, exists[0]))
            else:
                conn.execute("INSERT INTO atlas_master(atlas_name,category,content) VALUES(?,?,?)", (fname, cat, payload))
            stats['atlas_master'] += 1

        # Categories from V3 facility categories and high-level layers.
        cat_rows = []
        fc = v3.get('search_index', {}).get('facility_categories', {})
        for fa, mapped in fc.items():
            cat_rows.append(('bandarabbas_atlas_v3', mapped, fa))
        for cname in ['neighborhoods','roads','commercial_zones','ports','traffic_hotspots','knowledge_index']:
            cat_rows.append(('bandarabbas_atlas_v3', cname, 'verified source layer'))
        for atlas_name, cat_name, desc in cat_rows:
            if conn.execute("SELECT 1 FROM atlas_categories WHERE atlas_name=? AND category_name=?", (atlas_name, cat_name)).fetchone() is None:
                conn.execute("INSERT INTO atlas_categories(atlas_name,category_name,description) VALUES(?,?,?)", (atlas_name,cat_name,desc))
                stats['atlas_categories'] += 1

        # Resolve city id for Bandar Abbas if present.
        city_row = conn.execute("SELECT id FROM cities WHERE name=? LIMIT 1", (v3.get('city', {}).get('name', 'بندرعباس'),)).fetchone() if table_exists(conn, 'cities') else None
        city_id = city_row[0] if city_row else None
        bandarabbas_kid = knowledge_idx.get(norm(v3.get('city', {}).get('name', 'بندرعباس')))

        # Merge neighborhoods from V3 and V2 by normalized current_name.
        neighborhoods = {}
        for src in (v3, v2):
            for n in src.get('neighborhoods', []):
                key = norm(n.get('current_name'))
                if key and key not in neighborhoods:
                    neighborhoods[key] = n
        neighborhood_kids = {}
        for n in neighborhoods.values():
            name = n.get('current_name','').strip()
            existing = conn.execute("SELECT id FROM neighborhoods WHERE name=? LIMIT 1", (name,)).fetchone()
            if existing:
                nid = existing[0]
            else:
                conn.execute("INSERT INTO neighborhoods(city_id,name) VALUES(?,?)", (city_id, name))
                nid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                stats['neighborhoods'] += 1
            neighborhood_kids[norm(name)] = knowledge_idx.get(norm(name))
            if bandarabbas_kid:
                stats['edges'] += edge_insert(conn, seen_edges, neighborhood_kids[norm(name)], bandarabbas_kid, 'located_in_city', 1.0)
            for alias in list(n.get('old_names') or []):
                a_kid = knowledge_idx.get(norm(alias))
                n_kid = neighborhood_kids.get(norm(name))
                if a_kid and n_kid:
                    stats['edges'] += edge_insert(conn, seen_edges, a_kid, n_kid, 'alias_of', 1.0)

        # Roads from V3.
        for r in v3.get('streets', []):
            name = (r.get('name_fa') or '').strip()
            if not name:
                continue
            if conn.execute("SELECT 1 FROM roads WHERE name=? LIMIT 1", (name,)).fetchone() is None:
                conn.execute("INSERT INTO roads(name) VALUES(?)", (name,))
                stats['roads'] += 1
            rid = knowledge_idx.get(norm(name))
            if rid and bandarabbas_kid:
                stats['edges'] += edge_insert(conn, seen_edges, rid, bandarabbas_kid, 'located_in_city', 1.0)
            for alias in r.get('aliases') or []:
                a_kid = knowledge_idx.get(norm(alias))
                if a_kid and rid:
                    stats['edges'] += edge_insert(conn, seen_edges, a_kid, rid, 'alias_of', 1.0)

        # Places: facilities catalog, commercial zones, ports.
        def add_place(cat, name, lat=None, lon=None, source_id=None):
            if not name:
                return None
            pid = source_id or deterministic_place_id(cat, name)
            existing = conn.execute("SELECT id FROM places WHERE id=?", (pid,)).fetchone()
            if not existing:
                conn.execute("INSERT INTO places(id,cat,name,latitude,longitude) VALUES(?,?,?,?,?)", (pid,cat,name,lat,lon))
                stats['places'] += 1
            return pid

        # Facilities catalog.
        for section, items in (v3.get('facilities_catalog') or {}).items():
            if not isinstance(items, list):
                continue
            for item in items:
                name = item.get('name')
                add_place(section, name, item.get('latitude'), item.get('longitude'))
                sk = knowledge_idx.get(norm(name))
                nb = item.get('neighborhood')
                if sk and nb:
                    tk = knowledge_idx.get(norm(nb))
                    if tk:
                        stats['edges'] += edge_insert(conn, seen_edges, sk, tk, 'located_in_neighborhood', 1.0)

        # Commercial zones.
        for z in v3.get('commercial_zones') or []:
            name = z.get('name')
            add_place('commercial_zone', name, source_id=z.get('id'))
            sk = knowledge_idx.get(norm(name))
            nb = z.get('neighborhood')
            if sk and nb:
                tk = knowledge_idx.get(norm(nb))
                if tk:
                    stats['edges'] += edge_insert(conn, seen_edges, sk, tk, 'located_in_neighborhood', 1.0)

        # Ports and explicit island/route references.
        for p in v3.get('ports') or []:
            name = p.get('name')
            add_place('port', name, p.get('latitude'), p.get('longitude'), p.get('id'))
            sk = knowledge_idx.get(norm(name))
            for route in p.get('routes') or []:
                tk = knowledge_idx.get(norm(route))
                if sk and tk:
                    stats['edges'] += edge_insert(conn, seen_edges, sk, tk, 'serves_island', 1.0)

        # Explicit atlas layer links. Do NOT infer category-to-category links or full meshes.
        # Use only declared neighborhood membership and explicit aliases/location fields above.

        # Provenance / audit table.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS verified_import_audit (
                id INTEGER PRIMARY KEY,
                imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                file_name TEXT NOT NULL,
                sha256 TEXT NOT NULL,
                source_role TEXT NOT NULL,
                details TEXT
            )
        ''')
        files_meta = [
            (args.v3, 'verified_v3'),
            (args.v2, 'verified_v2'),
            (args.knowledge_index, 'verified_knowledge_index'),
        ]
        for path, role in files_meta:
            conn.execute(
                "INSERT INTO verified_import_audit(file_name,sha256,source_role,details) VALUES(?,?,?,?)",
                (os.path.basename(path), sha256_file(path), role, json.dumps(stats, ensure_ascii=False)),
            )

        conn.commit()

        after_edges = conn.execute('SELECT COUNT(*) FROM graph_edges').fetchone()[0]
        after_links = conn.execute('SELECT COUNT(*) FROM knowledge_links').fetchone()[0] if table_exists(conn, 'knowledge_links') else None
        integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
        foreign = conn.execute('PRAGMA foreign_key_check').fetchall()

        print('=== VERIFIED IMPORT COMPLETE ===')
        print(f'DB: {args.db}')
        print(f'BACKUP: {backup}')
        print(f'knowledge_links_before: {before_links}')
        print(f'knowledge_links_after:  {after_links}')
        print(f'graph_edges_before:     {before_edges}')
        print(f'graph_edges_after:      {after_edges}')
        print(f'new_neighborhood_rows:  {stats["neighborhoods"]}')
        print(f'new_road_rows:          {stats["roads"]}')
        print(f'new_place_rows:         {stats["places"]}')
        print(f'graph_edges_inserted:   {stats["edges"]}')
        print(f'integrity_check:        {integrity}')
        print(f'foreign_key_errors:     {len(foreign)}')
        if foreign:
            for row in foreign[:20]:
                print('FK_ERROR:', tuple(row))
            raise SystemExit(2)
        if integrity != 'ok':
            raise SystemExit(3)

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
