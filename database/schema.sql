-- ============================================================
-- Hermezgan Intelligent - Knowledge Graph Database Schema
-- Version: 1.0.0
-- ============================================================

-- ۱. جدول موجودیت‌ها (Entities)
CREATE TABLE IF NOT EXISTS entities (
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    type TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    description TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    latitude REAL,
    longitude REAL,
    established_year INTEGER,
    status TEXT DEFAULT 'active',
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ۲. جدول روابط (Relations)
CREATE TABLE IF NOT EXISTS relations (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    description TEXT,
    weight REAL DEFAULT 1.0,
    bidirectional INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    UNIQUE(source_id, target_id, relation_type)
);

-- ۳. جدول ویژگی‌ها (Properties)
CREATE TABLE IF NOT EXISTS entity_properties (
    property_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    property_key TEXT NOT NULL,
    property_value TEXT NOT NULL,
    data_type TEXT DEFAULT 'string',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id) ON DELETE CASCADE,
    UNIQUE(entity_id, property_key)
);

-- ۴. جدول گفتگوها (Chat History)
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    intent TEXT,
    entities_detected JSON,
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ۵. جدول بازخورد (Feedback)
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    user_id TEXT NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chat_history(chat_id) ON DELETE SET NULL
);

-- ایجاد ایندکس‌ها
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
CREATE INDEX IF NOT EXISTS idx_entities_category ON entities(category);
CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback(rating);