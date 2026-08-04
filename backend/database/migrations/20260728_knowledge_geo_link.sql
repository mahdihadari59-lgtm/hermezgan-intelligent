-- ============================================================
-- Migration: knowledge_geo_link
-- Created at: 2026-07-28
-- Description: Link knowledge base records to geo entities
-- ============================================================

-- ============================================================
-- UP Migration
-- ============================================================

CREATE TABLE IF NOT EXISTS knowledge_geo_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_id INTEGER NOT NULL,
    geo_table TEXT NOT NULL,
    geo_id INTEGER NOT NULL,
    relation_type TEXT DEFAULT 'related',
    confidence REAL DEFAULT 1.0,
    created_at INTEGER DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_kgl_knowledge
ON knowledge_geo_link(knowledge_id);

CREATE INDEX IF NOT EXISTS idx_kgl_geo
ON knowledge_geo_link(geo_table, geo_id);

-- ============================================================
-- DOWN Migration (Rollback)
-- ============================================================

DROP TABLE IF EXISTS knowledge_geo_link;
