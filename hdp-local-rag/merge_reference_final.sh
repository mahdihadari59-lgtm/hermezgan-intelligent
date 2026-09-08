#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

MASTER="$HOME/hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db"
HDP="$HOME/hermezgan-intelligent/backend/hdp_import_v4/hdp_knowledge.db"
GEO="$HOME/hermezgan-intelligent-backup-20260729/database/geo.db"

OUT="$HOME/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"

echo "============================================================"
echo "HORMOZGAN MASTER DATABASE - FINAL MERGE"
echo "============================================================"

for DB in "$MASTER" "$HDP" "$GEO"; do
    if [ ! -f "$DB" ]; then
        echo "ERROR: missing database:"
        echo "$DB"
        exit 1
    fi
done

echo
echo "[1/7] Creating master snapshot..."
rm -f "$OUT"
sqlite3 "$MASTER" "VACUUM INTO '$OUT';"

echo "[2/7] Attaching source databases..."

sqlite3 "$OUT" <<SQL

ATTACH DATABASE '$HDP' AS hdp;
ATTACH DATABASE '$GEO' AS geo;

PRAGMA foreign_keys=OFF;

BEGIN IMMEDIATE;

------------------------------------------------------------
-- HDP KNOWLEDGE
-- Tables that do not already exist in the master are copied
-- with their original names.
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS knowledge AS
SELECT * FROM hdp.knowledge
WHERE 0;

INSERT INTO knowledge
SELECT *
FROM hdp.knowledge
WHERE NOT EXISTS (
    SELECT 1 FROM main.knowledge m
    WHERE m.id = hdp.knowledge.id
);

CREATE TABLE IF NOT EXISTS knowledge_sources AS
SELECT * FROM hdp.knowledge_sources
WHERE 0;

INSERT INTO knowledge_sources
SELECT *
FROM hdp.knowledge_sources
WHERE NOT EXISTS (
    SELECT 1 FROM main.knowledge_sources m
    WHERE m.id = hdp.knowledge_sources.id
);

CREATE TABLE IF NOT EXISTS documents AS
SELECT * FROM hdp.documents
WHERE 0;

INSERT INTO documents
SELECT *
FROM hdp.documents
WHERE NOT EXISTS (
    SELECT 1 FROM main.documents m
    WHERE m.id = hdp.documents.id
);

------------------------------------------------------------
-- BANDARI KNOWLEDGE
-- Keep complete Bandari source data under explicit namespace.
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS bandari_vocabulary_master AS
SELECT * FROM hdp.bandari_vocabulary
WHERE 0;

INSERT INTO bandari_vocabulary_master
SELECT *
FROM hdp.bandari_vocabulary;

CREATE TABLE IF NOT EXISTS bandari_phrases_master AS
SELECT * FROM hdp.bandari_phrases
WHERE 0;

INSERT INTO bandari_phrases_master
SELECT *
FROM hdp.bandari_phrases;

CREATE TABLE IF NOT EXISTS bandari_grammar_master AS
SELECT * FROM hdp.bandari_grammar
WHERE 0;

INSERT INTO bandari_grammar_master
SELECT *
FROM hdp.bandari_grammar;

CREATE TABLE IF NOT EXISTS bandari_dialogues_master AS
SELECT * FROM hdp.bandari_dialogues
WHERE 0;

INSERT INTO bandari_dialogues_master
SELECT *
FROM hdp.bandari_dialogues;

CREATE TABLE IF NOT EXISTS bandari_proverbs_master AS
SELECT * FROM hdp.bandari_proverbs
WHERE 0;

INSERT INTO bandari_proverbs_master
SELECT *
FROM hdp.bandari_proverbs;

CREATE TABLE IF NOT EXISTS bandari_professional_terms_master AS
SELECT * FROM hdp.bandari_professional_terms
WHERE 0;

INSERT INTO bandari_professional_terms_master
SELECT *
FROM hdp.bandari_professional_terms;

CREATE TABLE IF NOT EXISTS bandari_texts_master AS
SELECT * FROM hdp.bandari_texts
WHERE 0;

INSERT INTO bandari_texts_master
SELECT *
FROM hdp.bandari_texts;

CREATE TABLE IF NOT EXISTS dialect_comparison_master AS
SELECT * FROM hdp.dialect_comparison
WHERE 0;

INSERT INTO dialect_comparison_master
SELECT *
FROM hdp.dialect_comparison;

CREATE TABLE IF NOT EXISTS dialect_info_master AS
SELECT * FROM hdp.dialect_info
WHERE 0;

INSERT INTO dialect_info_master
SELECT *
FROM hdp.dialect_info;

------------------------------------------------------------
-- GRAPH
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS graph_entities_master AS
SELECT * FROM hdp.graph_entities
WHERE 0;

INSERT INTO graph_entities_master
SELECT *
FROM hdp.graph_entities;

CREATE TABLE IF NOT EXISTS graph_entity_aliases_master AS
SELECT * FROM hdp.graph_entity_aliases
WHERE 0;

INSERT INTO graph_entity_aliases_master
SELECT *
FROM hdp.graph_entity_aliases;

CREATE TABLE IF NOT EXISTS graph_entity_attributes_master AS
SELECT * FROM hdp.graph_entity_attributes
WHERE 0;

INSERT INTO graph_entity_attributes_master
SELECT *
FROM hdp.graph_entity_attributes;

CREATE TABLE IF NOT EXISTS graph_relations_master AS
SELECT * FROM hdp.graph_relations
WHERE 0;

INSERT INTO graph_relations_master
SELECT *
FROM hdp.graph_relations;

CREATE TABLE IF NOT EXISTS graph_relation_types_master AS
SELECT * FROM hdp.graph_relation_types
WHERE 0;

INSERT INTO graph_relation_types_master
SELECT *
FROM hdp.graph_relation_types;

CREATE TABLE IF NOT EXISTS graph_nodes_master AS
SELECT * FROM hdp.graph_nodes
WHERE 0;

INSERT INTO graph_nodes_master
SELECT *
FROM hdp.graph_nodes;

CREATE TABLE IF NOT EXISTS graph_edges_master AS
SELECT * FROM hdp.graph_edges
WHERE 0;

INSERT INTO graph_edges_master
SELECT *
FROM hdp.graph_edges;

------------------------------------------------------------
-- GEO SOURCE
-- Keep GEO-only entities that are not represented by master.
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS geo_pois_master AS
SELECT * FROM geo.pois
WHERE 0;

INSERT INTO geo_pois_master
SELECT *
FROM geo.pois;

CREATE TABLE IF NOT EXISTS geo_roads_master AS
SELECT * FROM geo.roads
WHERE 0;

INSERT INTO geo_roads_master
SELECT *
FROM geo.roads;

CREATE TABLE IF NOT EXISTS geo_traffic_master AS
SELECT * FROM geo.traffic
WHERE 0;

INSERT INTO geo_traffic_master
SELECT *
FROM geo.traffic;

CREATE TABLE IF NOT EXISTS geo_reference_cameras_master AS
SELECT * FROM geo.cameras
WHERE 0;

INSERT INTO geo_reference_cameras_master
SELECT *
FROM geo.cameras;

------------------------------------------------------------
-- SOURCE REGISTRY
------------------------------------------------------------

CREATE TABLE IF NOT EXISTS master_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_path TEXT NOT NULL,
    source_role TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO master_sources
(source_name, source_path, source_role)
VALUES
(
    'hormozgan_geodata',
    '$MASTER',
    'PRIMARY_GEODATA'
),
(
    'hdp_knowledge',
    '$HDP',
    'KNOWLEDGE_RAG_GRAPH_BANDARI'
),
(
    'geo',
    '$GEO',
    'SECONDARY_GIS_REFERENCE'
);

COMMIT;

DETACH DATABASE hdp;
DETACH DATABASE geo;

PRAGMA foreign_keys=ON;

SQL

echo "[3/7] Integrity check..."
sqlite3 -readonly "$OUT" 'PRAGMA integrity_check;'

echo "[4/7] Foreign key check..."
sqlite3 -readonly "$OUT" 'PRAGMA foreign_key_check;'

echo "[5/7] Database size..."
ls -lh "$OUT"

echo "[6/7] Table count..."
sqlite3 -readonly "$OUT" \
"SELECT count(*) FROM sqlite_master
 WHERE type='table'
 AND name NOT LIKE 'sqlite_%';"

echo "[7/7] Source registry..."
sqlite3 -readonly "$OUT" \
"SELECT id, source_name, source_role
 FROM master_sources
 ORDER BY id;"

echo
echo "============================================================"
echo "FINAL MASTER CREATED"
echo "$OUT"
echo "============================================================"
