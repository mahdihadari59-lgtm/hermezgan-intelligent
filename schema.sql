CREATE TABLE places (
            id TEXT PRIMARY KEY,
            cat TEXT NOT NULL,
            name TEXT NOT NULL,
            lat REAL,
            lon REAL
        , osm_id TEXT, category TEXT, latitude REAL, longitude REAL);
CREATE TABLE knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
, keywords TEXT, source TEXT, priority INTEGER DEFAULT 1, subcategory TEXT, question TEXT, answer TEXT, city TEXT, lat REAL, lon REAL, updated_at DATETIME, category_fa TEXT, valid_until DATE, tags TEXT, topic TEXT, status TEXT DEFAULT 'active', subtopic TEXT, atlas TEXT, intent TEXT, main_intent TEXT, sub_intent TEXT, expert_name TEXT, is_deleted INTEGER DEFAULT 0, verified INTEGER DEFAULT 0, last_verified TEXT, confidence REAL, merged_into INTEGER, quality TEXT, entity_type TEXT, parent_id INTEGER, relation_type TEXT, graph_parent INTEGER, graph_depth INTEGER DEFAULT 0, graph_root TEXT, graph_path TEXT);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE category_mapping(
 code TEXT PRIMARY KEY,
 name_fa TEXT,
 search_weight INTEGER DEFAULT 1,
 icon TEXT
);
CREATE TABLE sqlite_stat1(tbl,idx,stat);
CREATE TABLE knowledge_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias_title TEXT NOT NULL,
    knowledge_id INTEGER NOT NULL
);
CREATE TABLE duplicate_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_id INTEGER,
    duplicate_count INTEGER,
    content_hash TEXT,
    reviewed INTEGER DEFAULT 0,
    keep_group INTEGER DEFAULT 1
);
CREATE TABLE aliases(
 id INTEGER PRIMARY KEY,
 alias TEXT,
 knowledge_id INTEGER
);
CREATE TABLE atlas_backup(
  id INT,
  title TEXT,
  category TEXT,
  content TEXT,
  created_at NUM,
  keywords TEXT,
  source TEXT,
  priority INT,
  subcategory TEXT,
  question TEXT,
  answer TEXT,
  city TEXT,
  lat REAL,
  lon REAL,
  updated_at NUM,
  category_fa TEXT,
  valid_until NUM,
  tags TEXT,
  topic TEXT
);
CREATE TABLE atlas_master (
    id INTEGER PRIMARY KEY,
    atlas_name TEXT,
    category TEXT,
    content LONGTEXT
);
CREATE TABLE knowledge_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE knowledge_links_backup(
  id INT,
  source_id INT,
  target_id INT,
  relation TEXT,
  confidence REAL,
  created_at NUM
);
CREATE TABLE knowledge_links_before_cleanup(
  id INT,
  source_id INT,
  target_id INT,
  relation TEXT,
  confidence REAL,
  created_at NUM
);
CREATE TABLE knowledge_links_auto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relation TEXT,
    confidence REAL
);
CREATE TABLE knowledge_links_smart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    confidence REAL DEFAULT 1.0
);
CREATE TABLE knowledge_topic_review (
    id INTEGER PRIMARY KEY,
    old_topic TEXT,
    new_topic TEXT,
    confidence REAL
);
CREATE TABLE knowledge_topic_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_id INTEGER,
    current_topic TEXT,
    suggested_topic TEXT,
    confidence REAL,
    reason TEXT
);
CREATE TABLE knowledge_graph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT,
    relation TEXT,
    target_entity TEXT,
    confidence REAL
);
CREATE TABLE knowledge_rank (
    knowledge_id INTEGER PRIMARY KEY,
    score REAL DEFAULT 0,
    incoming_links INTEGER DEFAULT 0,
    outgoing_links INTEGER DEFAULT 0,
    importance TEXT
, user_score REAL DEFAULT 0, final_score REAL DEFAULT 0, entity_weight REAL DEFAULT 0, topic_weight REAL DEFAULT 1, strategic_score REAL DEFAULT 0);
CREATE TABLE knowledge_intents (
    intent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_name TEXT,
    description TEXT
);
CREATE TABLE knowledge_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE,
    parent_category TEXT,
    description TEXT
);
CREATE TABLE knowledge_category_map (
    knowledge_id INTEGER,
    category_name TEXT,
    confidence REAL
);
CREATE TABLE question_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT,
    knowledge_id INTEGER,
    confidence REAL
);
CREATE TABLE topic_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT,
    target_topic TEXT,
    confidence REAL
);
CREATE TABLE auto_topic_fix (
    knowledge_id INTEGER,
    old_topic TEXT,
    new_topic TEXT,
    confidence REAL
);
CREATE TABLE intent_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_name TEXT NOT NULL,
    pattern TEXT NOT NULL,
    confidence REAL DEFAULT 0.90
);
CREATE TABLE entity_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT UNIQUE,
    description TEXT
);
CREATE TABLE conversation_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_message TEXT,
    detected_intent TEXT,
    detected_entity TEXT,
    response_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE response_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intent_name TEXT,
    template TEXT,
    priority INTEGER DEFAULT 1
);
CREATE TABLE duplicate_cleanup (
    old_id INTEGER,
    master_id INTEGER
);
CREATE TABLE master_knowledge (
    master_id INTEGER,
    duplicate_id INTEGER,
    confidence REAL
);
CREATE TABLE conversation_context (
    session_id TEXT PRIMARY KEY,
    last_intent TEXT,
    last_entity TEXT,
    last_topic TEXT,
    last_response_id INTEGER,
    updated_at TEXT
);
CREATE TABLE 'knowledge_search_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'knowledge_search_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'knowledge_search_content'(id INTEGER PRIMARY KEY, c0, c1, c2);
CREATE TABLE 'knowledge_search_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'knowledge_search_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE entity_aliases(
    entity_id INTEGER,
    alias TEXT,
    confidence REAL
);
CREATE TABLE user_feedback(
    id INTEGER PRIMARY KEY,
    knowledge_id INTEGER,
    click_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    dislike_count INTEGER DEFAULT 0
);
CREATE TABLE duplicate_cleanup_final(
  old_id INT,
  master_id
);
CREATE TABLE entity_weight(
    entity_type TEXT,
    weight REAL
);
CREATE TABLE topic_priority(
    topic TEXT PRIMARY KEY,
    weight REAL
);
CREATE TABLE query_routes(
    intent TEXT,
    target_source TEXT,
    priority INTEGER
);
CREATE TABLE entity_weights(
    entity_type TEXT PRIMARY KEY,
    weight REAL
);
CREATE TABLE entity_dictionary (
    id INTEGER PRIMARY KEY,
    entity TEXT,
    entity_type TEXT,
    city TEXT,
    importance INTEGER DEFAULT 1
);
CREATE TABLE graph_paths (
    source_id INTEGER,
    target_id INTEGER,
    depth INTEGER,
    score REAL
);
CREATE TABLE intent_entity_map(
    intent TEXT,
    entity_type TEXT,
    boost REAL
);
CREATE TABLE knowledge_hubs(id INT,title TEXT,size);
CREATE TABLE atlas_categories (
    id INTEGER PRIMARY KEY,
    atlas_name TEXT,
    category_name TEXT,
    description TEXT
);
CREATE TABLE atlas_stats (
    atlas_name TEXT PRIMARY KEY,
    direct_links INTEGER,
    total_nodes INTEGER,
    depth INTEGER
);
CREATE TABLE intent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_query TEXT,
    detected_intent TEXT,
    confidence REAL,
    expert_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE intent_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category TEXT,
    subcategory TEXT,

    main_intent TEXT,
    sub_intent TEXT,

    expert_name TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE router(
    id INTEGER PRIMARY KEY,
    main_intent TEXT UNIQUE,
    expert_name TEXT,
    fallback_expert TEXT,
    priority INTEGER DEFAULT 1
);
CREATE TABLE expert_dispatcher(
    expert_name TEXT PRIMARY KEY,
    description TEXT,
    priority_weight REAL DEFAULT 1.0,
    timeout_ms INTEGER DEFAULT 5000,
    is_active INTEGER DEFAULT 1
);
CREATE TABLE expert_mapping (
    expert_code TEXT PRIMARY KEY,
    expert_name TEXT NOT NULL
);
CREATE TABLE knowledge_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    weight INTEGER DEFAULT 1,
    source TEXT DEFAULT 'auto',
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id)
);
CREATE TABLE traffic_cameras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            lat REAL,
            lon REAL,
            camera_type TEXT,
            status TEXT DEFAULT 'active',
            install_date DATE,
            last_maintenance DATE,
            notes TEXT,
            knowledge_id INTEGER,
            FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
        );
CREATE TABLE traffic_blackspots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            lat REAL,
            lon REAL,
            severity INTEGER DEFAULT 3,
            accident_count INTEGER DEFAULT 0,
            fatal_count INTEGER DEFAULT 0,
            injury_count INTEGER DEFAULT 0,
            risk_factors TEXT,
            suggestions TEXT,
            last_updated DATE,
            knowledge_id INTEGER,
            FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
        );
CREATE TABLE traffic_accidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            accident_date DATETIME,
            lat REAL,
            lon REAL,
            severity TEXT,
            vehicles_involved INTEGER DEFAULT 0,
            fatalities INTEGER DEFAULT 0,
            injuries INTEGER DEFAULT 0,
            cause TEXT,
            weather_condition TEXT,
            road_condition TEXT,
            report_source TEXT,
            knowledge_id INTEGER,
            FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
        );
CREATE TABLE knowledge_stats (
            knowledge_id INTEGER PRIMARY KEY,
            tag_count INTEGER DEFAULT 0,
            entity_count INTEGER DEFAULT 0,
            relation_count INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
        );
CREATE TABLE knowledge_synonyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            synonym TEXT NOT NULL,
            category TEXT,
            weight INTEGER DEFAULT 1,
            UNIQUE(term, synonym)
        );
CREATE TABLE knowledge_dialects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dialect TEXT NOT NULL,
            formal TEXT NOT NULL,
            region TEXT,
            category TEXT,
            weight INTEGER DEFAULT 1,
            UNIQUE(dialect, formal)
        );
CREATE TABLE intent_routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            intent_pattern TEXT NOT NULL,
            target_table TEXT,
            target_column TEXT,
            priority INTEGER DEFAULT 5,
            description TEXT,
            UNIQUE(intent_pattern, target_table)
        );
CREATE TABLE 'traffic_cameras_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'traffic_cameras_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'traffic_cameras_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2);
CREATE TABLE 'traffic_cameras_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'traffic_cameras_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE 'traffic_blackspots_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'traffic_blackspots_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'traffic_blackspots_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);
CREATE TABLE 'traffic_blackspots_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'traffic_blackspots_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE 'knowledge_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'knowledge_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'knowledge_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4);
CREATE TABLE 'knowledge_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'knowledge_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE counties(
 id INTEGER PRIMARY KEY,
 name TEXT UNIQUE
);
CREATE TABLE districts(
 id INTEGER PRIMARY KEY,
 county_id INTEGER,
 name TEXT
);
CREATE TABLE roads(
 id INTEGER PRIMARY KEY,
 name TEXT
);
CREATE TABLE intersections(
 id INTEGER PRIMARY KEY,
 road_id INTEGER,
 name TEXT
);
CREATE TABLE cameras(
 id INTEGER PRIMARY KEY,
 title TEXT,
 type TEXT,
 neighborhood_id INTEGER,
 lat REAL,
 lon REAL
, status TEXT, city_id INTEGER, node_type TEXT DEFAULT 'entity', is_real INTEGER DEFAULT 1, node_level TEXT DEFAULT 'leaf', concept_type TEXT, camera_type TEXT, location_name TEXT);
CREATE TABLE accident_points(
 id INTEGER PRIMARY KEY,
 title TEXT,
 severity TEXT
);
CREATE TABLE hospitals(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER
);
CREATE TABLE clinics(
 id INTEGER PRIMARY KEY,
 name TEXT
);
CREATE TABLE pharmacies(
 id INTEGER PRIMARY KEY,
 name TEXT
);
CREATE TABLE schools(
 id INTEGER PRIMARY KEY,
 name TEXT
);
CREATE TABLE universities(
 id INTEGER PRIMARY KEY,
 name TEXT
);
CREATE TABLE attractions(
 id INTEGER PRIMARY KEY,
 name TEXT,
 type TEXT
);
CREATE TABLE businesses(
 id INTEGER PRIMARY KEY,
 name TEXT,
 business_type TEXT
);
CREATE TABLE geo_relations(
 id INTEGER PRIMARY KEY,
 source_type TEXT,
 source_id INTEGER,
 relation TEXT,
 target_type TEXT,
 target_id INTEGER
);
CREATE TABLE fuel_stations(
 id INTEGER PRIMARY KEY,
 name TEXT,
 fuel_type TEXT,
 city_id INTEGER
);
CREATE TABLE shopping_centers(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER
);
CREATE TABLE restaurants(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER
);
CREATE TABLE cafes(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER
);
CREATE TABLE hotels(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER,
 stars INTEGER
);
CREATE TABLE government_offices(
 id INTEGER PRIMARY KEY,
 name TEXT,
 city_id INTEGER
);
CREATE TABLE cities(
 id INTEGER PRIMARY KEY,
 county_id INTEGER,
 name TEXT UNIQUE
);
CREATE TABLE camera_entities(
 id INTEGER PRIMARY KEY,
 camera_id INTEGER,
 entity_type TEXT,
 entity_value TEXT
);
CREATE TABLE camera_locations(
 id INTEGER PRIMARY KEY,
 camera_id INTEGER,
 city TEXT,
 district TEXT,
 neighborhood TEXT,
 road_name TEXT,
 intersection_name TEXT
);
CREATE TABLE dialect_terms(
 id INTEGER PRIMARY KEY,
 term TEXT,
 meaning TEXT,
 example TEXT
);
CREATE TABLE proverbs(
 id INTEGER PRIMARY KEY,
 proverb TEXT,
 meaning TEXT
, usage_context TEXT);
CREATE TABLE local_foods(
 id INTEGER PRIMARY KEY,
 name TEXT,
 description TEXT
, origin TEXT, ingredients TEXT);
CREATE TABLE cultural_items(
 id INTEGER PRIMARY KEY,
 title TEXT,
 description TEXT
, item_type TEXT);
CREATE TABLE neighborhoods(
 id INTEGER PRIMARY KEY,
 city_id INTEGER,
 name TEXT UNIQUE
);
CREATE TABLE relation_types (
    relation_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT UNIQUE NOT NULL,
    description TEXT
);
CREATE TABLE medical_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    specialty TEXT,
    description TEXT,
    address TEXT,
    phone TEXT,
    latitude REAL,
    longitude REAL,
    is_24h INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE medical_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1.0
);
CREATE TABLE search_keywords(
    keyword TEXT,
    knowledge_id INTEGER
);
CREATE TABLE unified_search(
    term TEXT,
    knowledge_id INTEGER,
    score REAL DEFAULT 1
);
CREATE TABLE knowledge_graph_paths(
    source_id INTEGER,
    target_id INTEGER,
    distance INTEGER
);
CREATE TABLE cluster_rules(
    cluster_id INTEGER,
    pattern TEXT,
    relation_type TEXT DEFAULT 'contains',
    weight REAL DEFAULT 1
);
CREATE TABLE relation_rules(
    keyword TEXT,
    relation_type TEXT,
    target_pattern TEXT
, weight REAL DEFAULT 1);
CREATE TABLE semantic_relations(
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1,
    UNIQUE(source_id,target_id,relation_type)
);
CREATE TABLE expert_rules(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT UNIQUE,
    source_pattern TEXT,
    target_pattern TEXT,
    relation_type TEXT,
    weight REAL DEFAULT 1,
    priority INTEGER DEFAULT 1,
    enabled INTEGER DEFAULT 1
);
CREATE TABLE relation_candidates(
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,
    score REAL,
    rule_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE duplicate_candidates(
    source_id INTEGER,
    target_id INTEGER,
    reason TEXT,
    status TEXT DEFAULT 'pending'
);
CREATE TABLE entity_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    attribute_key TEXT NOT NULL,
    attribute_value TEXT,
    attribute_type TEXT,
    confidence REAL DEFAULT 1.0,
    source_knowledge_id INTEGER
);
CREATE TABLE entity_relations_graph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER,
    relation_type TEXT,
    target_entity_id INTEGER,
    weight REAL DEFAULT 1.0,
    source_knowledge_id INTEGER
);
CREATE TABLE extraction_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_id INTEGER,
    status TEXT DEFAULT 'pending',
    extracted_entities INTEGER DEFAULT 0,
    extracted_relations INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE graph_nodes(
 id INTEGER PRIMARY KEY,
 parent_id INTEGER,
 title TEXT,
 node_type TEXT,
 knowledge_id INTEGER
, depth INTEGER DEFAULT 0, root_id INTEGER, level INTEGER DEFAULT 0, path TEXT, children_count INTEGER DEFAULT 0, is_leaf INTEGER DEFAULT 0, score REAL DEFAULT 1.0, title_normalized TEXT);
CREATE TABLE graph_edges(
 id INTEGER PRIMARY KEY,
 source_id INTEGER,
 target_id INTEGER,
 relation_type TEXT
, weight REAL DEFAULT 1.0, confidence REAL DEFAULT 1.0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE hierarchy(
 id INTEGER PRIMARY KEY,
 parent_id INTEGER,
 child_id INTEGER,
 relation_type TEXT
);
CREATE TABLE neighborhood_graph (
    neighborhood_id INTEGER,
    neighborhood_name TEXT,
    parent_id INTEGER,
    parent_title TEXT,
    relation_type TEXT
);
CREATE TABLE neighborhood_master(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT UNIQUE,
 old_name TEXT,
 region TEXT,
 source_id INTEGER
);
CREATE TABLE neighborhood_links(
    neighborhood TEXT,
    knowledge_id INTEGER,
    title TEXT,
    relation_type TEXT
);
CREATE TABLE neighborhood_children(
    neighborhood_id INTEGER,
    child_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1
);
CREATE TABLE attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER,
    attr_key TEXT,
    attr_value TEXT
);
CREATE TABLE knowledge_clusters (
    id INTEGER PRIMARY KEY,
    cluster_id INTEGER,
    parent_id INTEGER,
    child_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1.0
);
CREATE TABLE knowledge_categories_master (
    id INTEGER PRIMARY KEY,
    category TEXT UNIQUE,
    parent_category TEXT,
    description TEXT
);
CREATE TABLE knowledge_children (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER NOT NULL,
    child_title TEXT NOT NULL,
    child_content TEXT,
    child_order INTEGER,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE knowledge_relations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_id INTEGER NOT NULL,

    target_id INTEGER NOT NULL,

    relation_type TEXT NOT NULL,

    weight REAL DEFAULT 1.0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(source_id) REFERENCES knowledge(id),

    FOREIGN KEY(target_id) REFERENCES knowledge(id)
);
CREATE TABLE knowledge_nodes (
    node_id INTEGER PRIMARY KEY,
    knowledge_id INTEGER,
    entity_type TEXT,
    canonical_name TEXT,
    parent_node INTEGER,
    FOREIGN KEY(knowledge_id) REFERENCES knowledge(id)
);
CREATE TABLE knowledge_edges (
    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node INTEGER,
    to_node INTEGER,
    relation TEXT,
    weight REAL DEFAULT 1,
    FOREIGN KEY(from_node) REFERENCES knowledge_nodes(node_id),
    FOREIGN KEY(to_node) REFERENCES knowledge_nodes(node_id)
);
CREATE TABLE graph_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id INTEGER,
    to_id INTEGER,
    relation TEXT,
    confidence REAL DEFAULT 1.0,
    source TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE entities(
    id INTEGER PRIMARY KEY,
    title TEXT,
    entity_type TEXT,
    parent_id INTEGER,
    level INTEGER,
    latitude REAL,
    longitude REAL,
    status TEXT
);
CREATE TABLE links(
    id INTEGER PRIMARY KEY,
    source_id INTEGER,
    target_id INTEGER,
    relation_type TEXT,
    weight REAL DEFAULT 1
);
CREATE TABLE police_stations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    district TEXT,
    description TEXT,
    lat REAL,
    lon REAL,
    category TEXT DEFAULT 'police',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE police_services (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    address TEXT,
    district TEXT,
    phone TEXT,
    code TEXT,
    phones TEXT,
    services TEXT,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    source TEXT,
    updated_at TEXT
);
CREATE TABLE knowledge_embeddings (
    knowledge_id INTEGER PRIMARY KEY,
    embedding BLOB NOT NULL,
    text_hash TEXT NOT NULL,
    model_version TEXT,
    dimension INTEGER DEFAULT 384,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE graph_properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    node_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY(node_id) REFERENCES graph_nodes(id)
                );
CREATE TABLE embeddings (
                    node_id INTEGER NOT NULL,
                    model_name TEXT NOT NULL,
                    vector_json TEXT NOT NULL,
                    dim INTEGER NOT NULL,
                    updated_at TEXT,
                    PRIMARY KEY (node_id, model_name)
                );
CREATE TABLE term_frequencies (
                    node_id INTEGER NOT NULL,
                    term TEXT NOT NULL,
                    tf INTEGER NOT NULL,
                    PRIMARY KEY (node_id, term)
                );
CREATE TABLE doc_length (
                    node_id INTEGER PRIMARY KEY,
                    length INTEGER NOT NULL
                );
CREATE TABLE corpus_stats (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
CREATE INDEX idx_cat
        ON places(cat)
        ;
CREATE INDEX idx_geo
        ON places(lat, lon)
        ;
CREATE INDEX idx_name
        ON places(name)
        ;
CREATE INDEX idx_knowledge_title
ON knowledge(title);
CREATE INDEX idx_knowledge_category
ON knowledge(category);
CREATE INDEX idx_knowledge_keywords
ON knowledge(keywords);
CREATE INDEX idx_knowledge_priority
ON knowledge(priority);
CREATE INDEX idx_knowledge_city
ON knowledge(city);
CREATE INDEX idx_knowledge_subcategory
ON knowledge(subcategory);
CREATE INDEX idx_knowledge_category_city
ON knowledge(category,city);
CREATE INDEX idx_title
ON knowledge(title);
CREATE INDEX idx_category
ON knowledge(category);
CREATE INDEX idx_keywords
ON knowledge(keywords);
CREATE INDEX idx_source
ON knowledge(source);
CREATE UNIQUE INDEX idx_links_unique
ON knowledge_links(
    source_id,
    target_id,
    relation
);
CREATE INDEX idx_knowledge_topic
ON knowledge(topic);
CREATE INDEX idx_graph_source
ON knowledge_graph(source_entity);
CREATE INDEX idx_graph_target
ON knowledge_graph(target_entity);
CREATE UNIQUE INDEX idx_alias_unique
ON knowledge_aliases(alias_title);
CREATE INDEX idx_intent_patterns
ON intent_patterns(intent_name);
CREATE INDEX idx_memory_session
ON conversation_memory(session_id);
CREATE INDEX idx_response_template
ON response_templates(intent_name);
CREATE INDEX idx_rank_score
ON knowledge_rank(score);
CREATE INDEX idx_rank_importance
ON knowledge_rank(importance);
CREATE INDEX idx_context_updated
ON conversation_context(updated_at);
CREATE INDEX idx_rank_final_score
ON knowledge_rank(final_score DESC);
CREATE INDEX idx_feedback_knowledge
ON user_feedback(knowledge_id);
CREATE INDEX idx_final_score
ON knowledge_rank(final_score);
CREATE INDEX idx_topic
ON knowledge(topic);
CREATE INDEX idx_target
ON knowledge_links(target_id);
CREATE INDEX idx_main_intent
ON knowledge(main_intent);
CREATE INDEX idx_sub_intent
ON knowledge(sub_intent);
CREATE INDEX idx_subcategory
ON knowledge(subcategory);
CREATE INDEX idx_city
ON knowledge(city);
CREATE INDEX idx_tags_knowledge_id ON knowledge_tags(knowledge_id);
CREATE INDEX idx_tags_tag ON knowledge_tags(tag);
CREATE INDEX idx_tags_kid ON knowledge_tags(knowledge_id);
CREATE INDEX idx_traffic_cameras_loc ON traffic_cameras(lat, lon);
CREATE INDEX idx_traffic_cameras_type ON traffic_cameras(camera_type);
CREATE INDEX idx_traffic_blackspots_loc ON traffic_blackspots(lat, lon);
CREATE INDEX idx_traffic_accidents_date ON traffic_accidents(accident_date);
CREATE INDEX idx_traffic_accidents_loc ON traffic_accidents(lat, lon);
CREATE INDEX idx_stats_kid ON knowledge_stats(knowledge_id);
CREATE INDEX idx_syn_term ON knowledge_synonyms(term);
CREATE INDEX idx_syn_syn ON knowledge_synonyms(synonym);
CREATE INDEX idx_dial_dialect ON knowledge_dialects(dialect);
CREATE INDEX idx_dial_formal ON knowledge_dialects(formal);
CREATE UNIQUE INDEX idx_camera_unique
ON traffic_cameras(name,lat,lon,camera_type);
CREATE INDEX idx_medical_name
ON medical_entities(name);
CREATE INDEX idx_medical_type
ON medical_entities(entity_type);
CREATE INDEX idx_medical_specialty
ON medical_entities(specialty);
CREATE INDEX idx_unified_term
ON unified_search(term);
CREATE INDEX idx_attr_entity
ON entity_attributes(entity_id);
CREATE INDEX idx_attr_key
ON entity_attributes(attribute_key);
CREATE INDEX idx_hierarchy_parent
ON hierarchy(parent_id);
CREATE INDEX idx_hierarchy_child
ON hierarchy(child_id);
CREATE INDEX idx_cluster_parent
ON knowledge_clusters(parent_id);
CREATE INDEX idx_cluster_child
ON knowledge_clusters(child_id);
CREATE UNIQUE INDEX idx_attr_unique
ON entity_attributes(
    entity_id,
    attribute_key
);
CREATE INDEX idx_children_parent
ON knowledge_children(parent_id);
CREATE INDEX idx_rel_source
ON knowledge_relations(source_id);
CREATE INDEX idx_rel_target
ON knowledge_relations(target_id);
CREATE INDEX idx_rel_type
ON knowledge_relations(relation_type);
CREATE INDEX idx_knowledge_parent

ON knowledge(parent_id);
CREATE INDEX idx_graph_edges_source
ON graph_edges(source_id);
CREATE INDEX idx_graph_edges_target
ON graph_edges(target_id);
CREATE INDEX idx_graph_edges_relation
ON graph_edges(relation_type);
CREATE INDEX idx_graph_nodes_knowledge
ON graph_nodes(knowledge_id);
CREATE INDEX idx_graph_nodes_title
ON graph_nodes(title);
CREATE INDEX idx_places_cat
ON places(cat);
CREATE INDEX idx_places_name
ON places(name);
CREATE INDEX idx_police_name
ON police_stations(name);
CREATE INDEX idx_police_district
ON police_stations(district);
CREATE INDEX idx_police_services_type
ON police_services(type);
CREATE INDEX idx_police_services_name
ON police_services(name);
CREATE INDEX idx_police_services_district
ON police_services(district);
CREATE INDEX idx_knowledge_embeddings_hash
ON knowledge_embeddings(text_hash);
CREATE INDEX idx_knowledge_embeddings_id
ON knowledge_embeddings(knowledge_id);
CREATE UNIQUE INDEX idx_nodes_title_normalized
ON graph_nodes(title_normalized);
CREATE INDEX idx_edges_source ON graph_edges(source_id);
CREATE INDEX idx_edges_target ON graph_edges(target_id);
CREATE UNIQUE INDEX idx_edges_unique ON graph_edges(source_id, target_id, relation_type);
CREATE INDEX idx_properties_node ON graph_properties(node_id);
CREATE INDEX idx_tf_term ON term_frequencies(term);
CREATE VIEW chatbot_search AS
SELECT
k.id,
k.title,
k.content,
k.topic,
r.score,
r.importance
FROM knowledge k
LEFT JOIN knowledge_rank r
ON k.id=r.knowledge_id
WHERE k.id NOT IN
(
   SELECT duplicate_id
   FROM master_knowledge
)
/* chatbot_search(id,title,content,topic,score,importance) */;
CREATE VIRTUAL TABLE knowledge_search
USING fts5(
    title,
    content,
    topic,
    tokenize='unicode61'
)
/* knowledge_search(title,content,topic) */;
CREATE VIEW intent_detector AS
SELECT
intent_name,
pattern,
confidence
FROM intent_patterns
ORDER BY confidence DESC
/* intent_detector(intent_name,pattern,confidence) */;
CREATE VIEW chatbot_ranked_search AS
SELECT
    k.id,
    k.title,
    k.topic,

    COALESCE(r.score,0)                AS base_score,
    COALESCE(r.strategic_score,0)      AS strategic_score,
    COALESCE(f.click_count,0)          AS click_count,
    COALESCE(f.like_count,0)           AS like_count,
    COALESCE(f.dislike_count,0)        AS dislike_count,

    (
        COALESCE(r.score,0) * 0.30
        + COALESCE(r.strategic_score,0) * 30
        + COALESCE(f.click_count,0) * 2
        + COALESCE(f.like_count,0) * 5
        - COALESCE(f.dislike_count,0) * 5
    ) AS final_score

FROM knowledge k

LEFT JOIN knowledge_rank r
ON k.id = r.knowledge_id

LEFT JOIN user_feedback f
ON k.id = f.knowledge_id
/* chatbot_ranked_search(id,title,topic,base_score,strategic_score,click_count,like_count,dislike_count,final_score) */;
CREATE VIEW chatbot_ai_search AS
SELECT
k.id,
k.title,
k.topic,

(
    COALESCE(r.score,0) * 0.30
    +
    COALESCE(r.strategic_score,0) * 30
    +
    CASE
        WHEN k.topic='traffic' THEN 50
        WHEN k.topic='tourism' THEN 30
        WHEN k.topic='medical' THEN 40
        WHEN k.topic='legal' THEN 20
        ELSE 0
    END
    +
    COALESCE(f.click_count,0) * 2
    +
    COALESCE(f.like_count,0) * 5
    -
    COALESCE(f.dislike_count,0) * 5

) AS final_score

FROM knowledge k
LEFT JOIN knowledge_rank r
ON k.id=r.knowledge_id
LEFT JOIN user_feedback f
ON k.id=f.knowledge_id
/* chatbot_ai_search(id,title,topic,final_score) */;
CREATE VIEW chatbot_best_answer AS
SELECT *
FROM knowledge k
WHERE k.id IN (
    SELECT MIN(id)
    FROM knowledge
    GROUP BY REPLACE(
        REPLACE(
            REPLACE(title,'؟',''),
        '?',''),
    '  ',' ')
)
/* chatbot_best_answer(id,title,category,content,created_at,keywords,source,priority,subcategory,question,answer,city,lat,lon,updated_at,category_fa,valid_until,tags,topic,status,subtopic,atlas,intent,main_intent,sub_intent,expert_name,is_deleted,verified,last_verified,confidence,merged_into,quality,entity_type,parent_id,relation_type,graph_parent,graph_depth,graph_root,graph_path) */;
CREATE VIEW v_intents AS
SELECT DISTINCT
    category AS main_intent,
    subcategory AS sub_intent
FROM knowledge
WHERE category IS NOT NULL
AND subcategory IS NOT NULL
/* v_intents(main_intent,sub_intent) */;
CREATE VIRTUAL TABLE traffic_cameras_fts
        USING fts5(
            camera_id UNINDEXED,
            name,
            location,
            tokenize='unicode61 remove_diacritics 0'
        )
/* traffic_cameras_fts(camera_id,name,location) */;
CREATE VIRTUAL TABLE traffic_blackspots_fts
        USING fts5(
            blackspot_id UNINDEXED,
            name,
            location,
            risk_factors,
            tokenize='unicode61 remove_diacritics 0'
        )
/* traffic_blackspots_fts(blackspot_id,name,location,risk_factors) */;
CREATE VIRTUAL TABLE knowledge_fts
        USING fts5(
            knowledge_id UNINDEXED,
            title,
            content,
            tags,
            entities,
            tokenize='unicode61 remove_diacritics 0'
        )
/* knowledge_fts(knowledge_id,title,content,tags,entities) */;
CREATE VIEW search_index AS
SELECT
    id,
    title,
    category
FROM knowledge

UNION

SELECT
    knowledge_id AS id,
    alias_title AS title,
    'alias'
FROM knowledge_aliases
/* search_index(id,title,category) */;
CREATE VIEW search_all AS
SELECT
    knowledge_id,
    term,
    score
FROM unified_search

UNION

SELECT
    knowledge_id,
    alias_title,
    5
FROM knowledge_aliases
/* search_all(knowledge_id,term,score) */;
CREATE VIEW knowledge_library AS
SELECT *
FROM knowledge
WHERE entity_type IN (
'document',
'guide',
'atlas',
'report'
)
/* knowledge_library(id,title,category,content,created_at,keywords,source,priority,subcategory,question,answer,city,lat,lon,updated_at,category_fa,valid_until,tags,topic,status,subtopic,atlas,intent,main_intent,sub_intent,expert_name,is_deleted,verified,last_verified,confidence,merged_into,quality,entity_type,parent_id,relation_type,graph_parent,graph_depth,graph_root,graph_path) */;
CREATE VIEW knowledge_entities AS
SELECT *
FROM knowledge
WHERE entity_type IN (
'province',
'county',
'city',
'neighborhood',
'street',
'place',
'restaurant',
'hotel',
'doctor'
)
/* knowledge_entities(id,title,category,content,created_at,keywords,source,priority,subcategory,question,answer,city,lat,lon,updated_at,category_fa,valid_until,tags,topic,status,subtopic,atlas,intent,main_intent,sub_intent,expert_name,is_deleted,verified,last_verified,confidence,merged_into,quality,entity_type,parent_id,relation_type,graph_parent,graph_depth,graph_root,graph_path) */;
CREATE TABLE duplicate_review (keep_id INTEGER, duplicate_id INTEGER, score REAL, status TEXT DEFAULT 'pending');
CREATE UNIQUE INDEX uq_duplicate_review_pair
        ON duplicate_review(keep_id, duplicate_id)
        ;
CREATE TABLE knowledge_chain (
    id INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    confidence REAL DEFAULT 1.0,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
