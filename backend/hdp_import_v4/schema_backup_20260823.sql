CREATE TABLE sources(id INTEGER PRIMARY KEY,source_name TEXT,sitemap TEXT,created_at TEXT);
CREATE TABLE documents(id INTEGER PRIMARY KEY,source_id INTEGER NOT NULL,url TEXT UNIQUE NOT NULL,final_url TEXT,canonical_url TEXT,title TEXT,business_name TEXT,meta_description TEXT,og_title TEXT,og_description TEXT,language TEXT,text_summary TEXT,content TEXT,word_count INTEGER DEFAULT 0,address TEXT,phone TEXT,mobile TEXT,website TEXT,latitude REAL,longitude REAL,postal_code TEXT,district TEXT,petrography TEXT,status_code INTEGER,fetched_at TEXT,raw_html_file TEXT,content_hash TEXT,error TEXT,image_count INTEGER DEFAULT 0, category TEXT);
CREATE TABLE images(id INTEGER PRIMARY KEY,document_id INTEGER NOT NULL,image_url TEXT NOT NULL,local_file TEXT,filename TEXT,status TEXT,size INTEGER DEFAULT 0,UNIQUE(document_id,image_url));
CREATE TABLE sqlite_stat1(tbl,idx,stat);
CREATE INDEX idx_doc_business ON documents(business_name);
CREATE INDEX idx_doc_phone ON documents(phone);
CREATE INDEX idx_doc_mobile ON documents(mobile);
CREATE INDEX idx_doc_coords ON documents(latitude,longitude);
CREATE VIEW v_business_directory AS
SELECT 
    id,
    title,
    business_name,
    address,
    phone,
    latitude,
    longitude,
    image_count,
    substr(content, 1, 200) as preview
FROM documents
WHERE business_name IS NOT NULL OR title LIKE '%بهترین%'
/* v_business_directory(id,title,business_name,address,phone,latitude,longitude,image_count,preview) */;
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT,
    parent_id INTEGER
);
CREATE VIEW v_business_full AS
SELECT 
    d.id,
    d.title,
    d.business_name,
    d.category,
    d.address,
    d.phone,
    d.latitude,
    d.longitude,
    d.district,
    (SELECT COUNT(*) FROM images WHERE document_id = d.id) as image_count,
    d.content
FROM documents d
WHERE d.business_name IS NOT NULL OR d.title LIKE '%بهترین%'
/* v_business_full(id,title,business_name,category,address,phone,latitude,longitude,district,image_count,content) */;
CREATE VIEW v_district_stats AS
SELECT 
    district,
    COUNT(*) as total_businesses,
    COUNT(DISTINCT category) as category_types,
    COUNT(CASE WHEN phone IS NOT NULL THEN 1 END) as has_phone,
    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as has_location
FROM documents
WHERE district IS NOT NULL AND district != ''
GROUP BY district
ORDER BY total_businesses DESC
/* v_district_stats(district,total_businesses,category_types,has_phone,has_location) */;
CREATE VIEW v_search_index AS
SELECT 
    id,
    title,
    business_name,
    category,
    address,
    phone,
    district,
    content_preview
FROM (
    SELECT 
        id,
        title,
        business_name,
        category,
        address,
        phone,
        district,
        substr(content, 1, 300) as content_preview
    FROM documents
) 
WHERE business_name IS NOT NULL OR title IS NOT NULL
/* v_search_index(id,title,business_name,category,address,phone,district,content_preview) */;
CREATE TABLE graph_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- 'place', 'person', 'organization', 'concept', 'event'
    name TEXT NOT NULL,
    description TEXT,
    source_id INTEGER,  -- ارجاع به جدول sources
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE INDEX idx_graph_entities_type ON graph_entities(entity_type);
CREATE INDEX idx_graph_entities_name ON graph_entities(name);
CREATE TABLE graph_relation_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,  -- 'located_in', 'part_of', 'managed_by', etc.
    label_fa TEXT NOT NULL,
    label_en TEXT,
    description TEXT,
    is_bidirectional BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_relation_types_code ON graph_relation_types(code);
CREATE TABLE graph_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity_id INTEGER NOT NULL,
    target_entity_id INTEGER NOT NULL,
    relation_type_id INTEGER NOT NULL,
    weight REAL DEFAULT 1.0,  -- وزن رابطه (برای جستجوی معنایی)
    confidence REAL DEFAULT 0.8,  -- اطمینان از صحت رابطه
    metadata TEXT,  -- JSON برای اطلاعات اضافی
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (target_entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (relation_type_id) REFERENCES graph_relation_types(id)
);
CREATE INDEX idx_graph_relations_source ON graph_relations(source_entity_id);
CREATE INDEX idx_graph_relations_target ON graph_relations(target_entity_id);
CREATE INDEX idx_graph_relations_type ON graph_relations(relation_type_id);
CREATE TABLE graph_entity_attributes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    attribute_key TEXT NOT NULL,  -- 'population', 'area', 'founded_year', etc.
    attribute_value TEXT NOT NULL,
    attribute_type TEXT DEFAULT 'string',  -- 'string', 'number', 'date', 'boolean', 'json'
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    UNIQUE(entity_id, attribute_key)
);
CREATE INDEX idx_entity_attributes_key ON graph_entity_attributes(attribute_key);
CREATE TABLE graph_entity_aliases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    alias_name TEXT NOT NULL,
    language TEXT DEFAULT 'fa',
    is_primary BOOLEAN DEFAULT 0,
    FOREIGN KEY (entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    UNIQUE(entity_id, alias_name)
);
CREATE INDEX idx_entity_aliases_name ON graph_entity_aliases(alias_name);
CREATE TABLE graph_cooccurrence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity1_id INTEGER NOT NULL,
    entity2_id INTEGER NOT NULL,
    document_id INTEGER,
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity1_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (entity2_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(entity1_id, entity2_id, document_id)
);
CREATE INDEX idx_cooccurrence_entities ON graph_cooccurrence(entity1_id, entity2_id);
CREATE TABLE graph_document_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 0.5,
    mention_count INTEGER DEFAULT 1,
    positions TEXT,  -- JSON آرایه‌ای از موقعیت‌های اشاره در متن
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(entity_id, document_id)
);
CREATE INDEX idx_doc_mapping_entity ON graph_document_mapping(entity_id);
CREATE INDEX idx_doc_mapping_document ON graph_document_mapping(document_id);
CREATE TABLE graph_image_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    caption TEXT,
    is_featured BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entity_id) REFERENCES graph_entities(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    UNIQUE(entity_id, image_id)
);
CREATE INDEX idx_image_mapping_entity ON graph_image_mapping(entity_id);
CREATE VIEW v_graph_entity_network AS
SELECT 
    e1.name as source_name,
    e1.entity_type as source_type,
    rt.label_fa as relation,
    e2.name as target_name,
    e2.entity_type as target_type,
    r.weight,
    r.confidence
FROM graph_relations r
JOIN graph_entities e1 ON r.source_entity_id = e1.id
JOIN graph_entities e2 ON r.target_entity_id = e2.id
JOIN graph_relation_types rt ON r.relation_type_id = rt.id
/* v_graph_entity_network(source_name,source_type,relation,target_name,target_type,weight,confidence) */;
CREATE VIEW v_graph_place_entities AS
SELECT 
    e.id,
    e.name,
    e.entity_type,
    e.description,
    ea.attribute_key,
    ea.attribute_value
FROM graph_entities e
LEFT JOIN graph_entity_attributes ea ON e.id = ea.entity_id
WHERE e.entity_type = 'place'
ORDER BY e.name
/* v_graph_place_entities(id,name,entity_type,description,attribute_key,attribute_value) */;
CREATE VIEW v_graph_stats AS
SELECT 
    (SELECT COUNT(*) FROM graph_entities) as total_entities,
    (SELECT COUNT(*) FROM graph_relations) as total_relations,
    (SELECT COUNT(*) FROM graph_relation_types) as relation_types,
    (SELECT entity_type, COUNT(*) as count FROM graph_entities GROUP BY entity_type) as entity_counts
/* v_graph_stats(total_entities,total_relations,relation_types,entity_counts) */;
CREATE TABLE economy_industry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    activity TEXT,
    location TEXT,
    employees TEXT,
    product TEXT
);
CREATE TABLE education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    students TEXT
);
CREATE TABLE neighborhoods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    old_name TEXT,
    zone TEXT,
    district TEXT,
    texture TEXT
);
CREATE TABLE piers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    distance_km TEXT,
    travel_time TEXT
);
CREATE TABLE sports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    capacity TEXT
);
CREATE TABLE treatment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    zone TEXT,
    beds TEXT
);
CREATE TABLE "urban_zones" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone TEXT,
    local_name TEXT,
    neighborhoods TEXT,
    population TEXT,
    feature TEXT,
    infrastructure TEXT
);
CREATE TABLE hospitals (
    name TEXT,
    type TEXT,
    district TEXT,
    feature TEXT,
    bed_status TEXT
);
CREATE TABLE shopping_centers (
    name TEXT,
    type TEXT,
    location TEXT,
    size TEXT,
    hours TEXT,
    feature TEXT
);
CREATE TABLE parks_recreation (
    name TEXT,
    type TEXT,
    location TEXT,
    feature TEXT
);
CREATE TABLE universities (
    name TEXT,
    type TEXT,
    location TEXT,
    majors TEXT,
    students TEXT
);
CREATE TABLE industries (
    name TEXT,
    activity TEXT,
    location TEXT,
    employees TEXT
);
CREATE TABLE religious_sites (
    name TEXT,
    type TEXT,
    location TEXT,
    feature TEXT
);
CREATE TABLE government_offices (
    name TEXT,
    service TEXT,
    location TEXT
);
CREATE TABLE hotels (
    name TEXT,
    grade TEXT,
    location TEXT,
    feature TEXT
);
CREATE TABLE informal_settlements (
    indicator TEXT,
    value TEXT,
    description TEXT
);
CREATE TABLE gis_coordinates (
    name TEXT,
    latitude REAL,
    longitude REAL,
    type TEXT
);
CREATE TABLE city_info (
    indicator TEXT,
    value TEXT
);
CREATE TABLE history (
    period TEXT,
    year TEXT,
    event TEXT,
    population TEXT
);
CREATE INDEX idx_hospitals_name ON hospitals(name);
CREATE INDEX idx_shopping_name ON shopping_centers(name);
CREATE INDEX idx_neighborhoods_name ON neighborhoods(name);
CREATE INDEX idx_gis_name ON gis_coordinates(name);
CREATE VIEW v_city_overview AS
SELECT 
    'بیمارستان' as category,
    name,
    district as location,
    feature as description
FROM hospitals
UNION ALL
SELECT 
    'مرکز خرید',
    name,
    location,
    feature
FROM shopping_centers
UNION ALL
SELECT 
    'پارک',
    name,
    location,
    feature
FROM parks_recreation
UNION ALL
SELECT 
    'دانشگاه',
    name,
    location,
    majors
FROM universities
UNION ALL
SELECT 
    'صنعت',
    name,
    location,
    activity
FROM industries
UNION ALL
SELECT 
    'مکان مذهبی',
    name,
    location,
    feature
FROM religious_sites
/* v_city_overview(category,name,location,description) */;
CREATE VIEW v_zone_statistics AS
SELECT 
    u.zone,
    u.local_name,
    u.population,
    u.feature,
    u.infrastructure,
    COUNT(DISTINCT h.name) as hospitals,
    COUNT(DISTINCT s.name) as shopping_centers,
    COUNT(DISTINCT p.name) as parks,
    COUNT(DISTINCT n.name) as neighborhoods
FROM urban_zones u
LEFT JOIN hospitals h ON h.district LIKE '%' || u.zone || '%'
LEFT JOIN shopping_centers s ON s.location LIKE '%' || u.zone || '%'
LEFT JOIN parks_recreation p ON p.location LIKE '%' || u.zone || '%'
LEFT JOIN neighborhoods n ON n.zone = u.zone
GROUP BY u.zone
/* v_zone_statistics(zone,local_name,population,feature,infrastructure,hospitals,shopping_centers,parks,neighborhoods) */;
CREATE VIEW v_rag_search AS
SELECT 
    'hospitals' as table_name,
    id,
    name as title,
    feature as content,
    district as location,
    type as category,
    bed_status as status
FROM hospitals

UNION ALL

SELECT 
    'shopping_centers',
    id,
    name,
    feature,
    location,
    type,
    hours
FROM shopping_centers

UNION ALL

SELECT 
    'parks_recreation',
    id,
    name,
    feature,
    location,
    type,
    NULL
FROM parks_recreation

UNION ALL

SELECT 
    'universities',
    id,
    name,
    majors,
    location,
    type,
    students
FROM universities

UNION ALL

SELECT 
    'industries',
    id,
    name,
    activity,
    location,
    'صنعتی',
    employees
FROM industries

UNION ALL

SELECT 
    'religious_sites',
    id,
    name,
    feature,
    location,
    type,
    NULL
FROM religious_sites

UNION ALL

SELECT 
    'neighborhoods',
    id,
    name,
    texture,
    zone,
    'محله',
    NULL
FROM neighborhoods;
CREATE INDEX idx_hospitals_district ON hospitals(district);
CREATE INDEX idx_hospitals_feature ON hospitals(feature);
CREATE INDEX idx_shopping_location ON shopping_centers(location);
CREATE INDEX idx_shopping_feature ON shopping_centers(feature);
CREATE INDEX idx_parks_name ON parks_recreation(name);
CREATE INDEX idx_parks_location ON parks_recreation(location);
CREATE INDEX idx_parks_type ON parks_recreation(type);
CREATE INDEX idx_universities_name ON universities(name);
CREATE INDEX idx_universities_location ON universities(location);
CREATE INDEX idx_universities_majors ON universities(majors);
CREATE INDEX idx_industries_name ON industries(name);
CREATE INDEX idx_industries_location ON industries(location);
CREATE INDEX idx_industries_activity ON industries(activity);
CREATE INDEX idx_religious_name ON religious_sites(name);
CREATE INDEX idx_religious_location ON religious_sites(location);
CREATE INDEX idx_religious_type ON religious_sites(type);
CREATE INDEX idx_neighborhoods_zone ON neighborhoods(zone);
CREATE INDEX idx_neighborhoods_texture ON neighborhoods(texture);
CREATE INDEX idx_gis_type ON gis_coordinates(type);
CREATE INDEX idx_gis_lat_lon ON gis_coordinates(latitude, longitude);
CREATE INDEX idx_urban_zones_zone ON urban_zones(zone);
CREATE INDEX idx_urban_zones_population ON urban_zones(population);
CREATE INDEX idx_hotels_name ON hotels(name);
CREATE INDEX idx_hotels_grade ON hotels(grade);
CREATE INDEX idx_hotels_location ON hotels(location);
CREATE VIRTUAL TABLE rag_fts USING fts5(
    table_name,
    record_id,
    title,
    content,
    location,
    category
)
/* rag_fts(table_name,record_id,title,content,location,category) */;
CREATE TABLE 'rag_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'rag_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'rag_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5);
CREATE TABLE 'rag_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'rag_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE knowledge (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    city TEXT,
    province TEXT DEFAULT 'هرمزگان',
    source TEXT,
    source_url TEXT,
    source_type TEXT,
    data_period TEXT,
    verification_status TEXT DEFAULT 'needs_verification',
    confidence REAL,
    keywords TEXT,
    priority INTEGER DEFAULT 5,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE traffic_cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT DEFAULT 'بندرعباس',
    province TEXT DEFAULT 'هرمزگان',
    camera_type TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    address TEXT,
    status TEXT,
    active_from TEXT,
    source_id TEXT,
    verification_status TEXT DEFAULT 'needs_verification',
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE traffic_accidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TEXT,
    city TEXT DEFAULT 'بندرعباس',
    province TEXT DEFAULT 'هرمزگان',
    road_name TEXT,
    latitude REAL,
    longitude REAL,
    accident_type TEXT,
    severity TEXT,
    fatalities INTEGER DEFAULT 0,
    injuries INTEGER DEFAULT 0,
    cause TEXT,
    vehicle_type TEXT,
    source_id TEXT,
    verification_status TEXT DEFAULT 'needs_verification',
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE traffic_blackspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT DEFAULT 'بندرعباس',
    province TEXT DEFAULT 'هرمزگان',
    road_name TEXT,
    latitude REAL,
    longitude REAL,
    risk_level TEXT,
    accident_count INTEGER,
    fatalities INTEGER,
    injuries INTEGER,
    intervention_status TEXT,
    source_id TEXT,
    verification_status TEXT DEFAULT 'needs_verification',
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE knowledge_sources (
    id TEXT PRIMARY KEY,
    publisher TEXT,
    title TEXT,
    url TEXT,
    source_type TEXT,
    publication_date TEXT,
    accessed_at TEXT,
    reliability_level TEXT
);
CREATE TABLE graph_nodes (
    id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    label TEXT NOT NULL,
    entity_id TEXT,
    metadata_json TEXT
);
CREATE TABLE graph_edges (
    id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    metadata_json TEXT,
    FOREIGN KEY(source_node_id) REFERENCES graph_nodes(id),
    FOREIGN KEY(target_node_id) REFERENCES graph_nodes(id)
);
CREATE INDEX idx_knowledge_city ON knowledge(city);
CREATE INDEX idx_knowledge_category ON knowledge(category);
CREATE INDEX idx_cameras_city ON traffic_cameras(city);
CREATE INDEX idx_accidents_city ON traffic_accidents(city);
CREATE INDEX idx_blackspots_city ON traffic_blackspots(city);
CREATE INDEX idx_edges_source ON graph_edges(source_node_id);
CREATE INDEX idx_edges_target ON graph_edges(target_node_id);
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE cafes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE parks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE fuel_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE police_stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    address TEXT,
    lat REAL,
    lng REAL,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_restaurants_name ON restaurants(name);
CREATE INDEX idx_schools_name ON schools(name);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_fuel_stations_type ON fuel_stations(type);
CREATE INDEX idx_restaurants_location ON restaurants(location);
CREATE INDEX idx_schools_location ON schools(location);
CREATE INDEX idx_cafes_name ON cafes(name);
CREATE INDEX idx_cafes_location ON cafes(location);
CREATE INDEX idx_fuel_stations_name ON fuel_stations(name);
CREATE INDEX idx_fuel_stations_location ON fuel_stations(location);
CREATE INDEX idx_police_stations_name ON police_stations(name);
CREATE INDEX idx_police_stations_location ON police_stations(location);
CREATE INDEX idx_cameras_name ON cameras(name);
CREATE INDEX idx_cameras_type ON cameras(type);
CREATE TABLE accident_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lat REAL,
    lon REAL,
    accident_type TEXT,
    severity TEXT,
    cause TEXT,
    suggestion TEXT,
    rank INTEGER,
    accidents INTEGER,
    fatalities INTEGER,
    injuries INTEGER,
    year INTEGER,
    source TEXT,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE traffic_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    road_name TEXT,
    road_osm_id BIGINT,
    lat REAL,
    lon REAL,
    speed_kmh REAL,
    congestion_level TEXT,
    timestamp TIMESTAMP,
    source TEXT
);
CREATE TABLE traffic_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE,
    device_type TEXT,
    location TEXT,
    lat REAL,
    lon REAL,
    road_name TEXT,
    status TEXT,
    source TEXT,
    installation_date TIMESTAMP,
    last_maintenance TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT,
    destination TEXT,
    route TEXT,
    normal_time TEXT,
    peak_time TEXT,
    distance REAL,
    condition TEXT,
    safety_score REAL,
    hotspot_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE alternative_routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    main_route TEXT,
    alternative_route TEXT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE traffic_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    category TEXT,
    city TEXT DEFAULT 'بندرعباس',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE hotspots_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    severity INTEGER,
    accidents INTEGER,
    fatalities INTEGER,
    injuries INTEGER,
    accident_type TEXT,
    cause TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE transport_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    osm_id BIGINT,
    name TEXT,
    name_fa TEXT,
    transport_type TEXT,
    operator TEXT,
    network TEXT,
    lat REAL,
    lon REAL,
    city TEXT,
    district TEXT,
    route_number TEXT,
    schedule TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE backup_accident_hotspots(
  id INT,
  name TEXT,
  lat REAL,
  lon REAL,
  accident_type TEXT,
  severity TEXT,
  cause TEXT,
  suggestion TEXT,
  rank INT,
  accidents INT,
  fatalities INT,
  injuries INT,
  year INT,
  source TEXT,
  last_updated NUM,
  created_at NUM
);
CREATE TABLE backup_traffic_data(
  id INT,
  road_name TEXT,
  road_osm_id INT,
  lat REAL,
  lon REAL,
  speed_kmh REAL,
  congestion_level TEXT,
  timestamp NUM,
  source TEXT
);
CREATE TABLE backup_traffic_devices(
  id INT,
  device_id TEXT,
  device_type TEXT,
  location TEXT,
  lat REAL,
  lon REAL,
  road_name TEXT,
  status TEXT,
  source TEXT,
  installation_date NUM,
  last_maintenance NUM,
  collected_at NUM
);
CREATE TABLE backup_routes(
  id INT,
  origin TEXT,
  destination TEXT,
  route TEXT,
  normal_time TEXT,
  peak_time TEXT,
  distance REAL,
  condition TEXT,
  safety_score REAL,
  hotspot_count INT,
  created_at NUM
);
CREATE TABLE backup_alternative_routes(
  id INT,
  main_route TEXT,
  alternative_route TEXT,
  reason TEXT,
  created_at NUM
);
CREATE TABLE backup_traffic_info(
  id INT,
  title TEXT,
  content TEXT,
  category TEXT,
  city TEXT,
  created_at NUM
);
CREATE TABLE backup_hotspots_info(
  id INT,
  name TEXT,
  location TEXT,
  severity INT,
  accidents INT,
  fatalities INT,
  injuries INT,
  accident_type TEXT,
  cause TEXT,
  created_at NUM
);
CREATE VIEW v_safety_report AS
SELECT 
    h.name as hotspot_name,
    h.severity,
    h.accidents,
    h.fatalities,
    h.injuries,
    h.cause,
    h.suggestion,
    COUNT(DISTINCT d.id) as devices_installed,
    CASE 
        WHEN COUNT(DISTINCT d.id) = 0 THEN '⚠️ نیاز فوری به تجهیزات'
        WHEN COUNT(DISTINCT d.id) < 2 THEN '⚡ نیاز به تجهیزات بیشتر'
        ELSE '✅ تجهیزات مناسب'
    END as equipment_status
FROM accident_hotspots h
LEFT JOIN traffic_devices d ON d.road_name LIKE '%' || h.name || '%'
GROUP BY h.id
ORDER BY h.severity DESC, h.accidents DESC
/* v_safety_report(hotspot_name,severity,accidents,fatalities,injuries,cause,suggestion,devices_installed,equipment_status) */;
CREATE VIEW v_route_safety AS
SELECT 
    origin || ' → ' || destination as route_name,
    route,
    distance,
    normal_time,
    peak_time,
    safety_score,
    hotspot_count,
    condition,
    CASE 
        WHEN safety_score >= 8 THEN '✅ بسیار ایمن'
        WHEN safety_score >= 7 THEN '✓ ایمن'
        WHEN safety_score >= 6 THEN '⚠️ نیاز به احتیاط'
        ELSE '🔴 پرخطر'
    END as safety_label
FROM routes
ORDER BY safety_score DESC
/* v_route_safety(route_name,route,distance,normal_time,peak_time,safety_score,hotspot_count,condition,safety_label) */;
CREATE VIEW v_safety_analysis AS
SELECT 
    h.id,
    h.name,
    h.severity,
    h.accidents,
    h.fatalities,
    h.injuries,
    h.cause,
    h.suggestion,
    COUNT(d.id) as device_count,
    GROUP_CONCAT(DISTINCT d.device_type) as device_types,
    ROUND(AVG(td.speed_kmh), 1) as avg_speed,
    CASE 
        WHEN COUNT(d.id) = 0 THEN 'بدون پوشش'
        WHEN COUNT(d.id) < 2 THEN 'پوشش ناقص'
        ELSE 'پوشش کامل'
    END as coverage_status,
    CASE 
        WHEN h.fatalities > 10 THEN 'بحرانی'
        WHEN h.fatalities > 5 THEN 'پرخطر'
        WHEN h.fatalities > 2 THEN 'متوسط'
        ELSE 'کم خطر'
    END as risk_level
FROM accident_hotspots h
LEFT JOIN traffic_devices d ON d.road_name LIKE '%' || h.name || '%'
LEFT JOIN traffic_data td ON td.road_name LIKE '%' || h.name || '%'
GROUP BY h.id
ORDER BY h.severity DESC, h.accidents DESC
/* v_safety_analysis(id,name,severity,accidents,fatalities,injuries,cause,suggestion,device_count,device_types,avg_speed,coverage_status,risk_level) */;
CREATE TABLE dialect_info (
    code TEXT PRIMARY KEY,
    name_fa TEXT NOT NULL,
    name_en TEXT,
    region TEXT,
    population_estimate INTEGER,
    is_verified BOOLEAN DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    notes TEXT
);
CREATE TABLE bandari_categories (
    code TEXT PRIMARY KEY,
    label_fa TEXT NOT NULL,
    label_en TEXT,
    parent_code TEXT,
    description TEXT,
    icon TEXT,
    sort_order INTEGER DEFAULT 0
);
CREATE TABLE bandari_vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_standard TEXT NOT NULL,
    word_bandari TEXT NOT NULL,
    word_english TEXT,
    phonetic_ipa TEXT,
    part_of_speech TEXT,
    category TEXT,
    subcategory TEXT,
    definition TEXT,
    etymology TEXT,
    cultural_note TEXT,
    example_bandari TEXT,
    example_persian TEXT,
    example_english TEXT,
    dialect_code TEXT DEFAULT 'ban',
    dialect_variant TEXT DEFAULT 'بندرعباس',
    confidence_score INTEGER DEFAULT 70,
    data_quality TEXT DEFAULT 'sourced',
    is_loanword BOOLEAN DEFAULT 0,
    source_reference TEXT,
    related_poi_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_vocab_standard ON bandari_vocabulary(word_standard);
CREATE INDEX idx_vocab_bandari ON bandari_vocabulary(word_bandari);
CREATE INDEX idx_vocab_category ON bandari_vocabulary(category);
CREATE INDEX idx_vocab_dialect ON bandari_vocabulary(dialect_code);
CREATE INDEX idx_vocab_quality ON bandari_vocabulary(data_quality);
CREATE TABLE bandari_phrases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase_bandari TEXT NOT NULL,
    phrase_persian TEXT NOT NULL,
    phrase_english TEXT,
    category TEXT,
    context TEXT,
    dialect_code TEXT DEFAULT 'ban',
    confidence_score INTEGER DEFAULT 85,
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_phrase_bandari ON bandari_phrases(phrase_bandari);
CREATE INDEX idx_phrase_category ON bandari_phrases(category);
CREATE TABLE bandari_proverbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proverb_bandari TEXT NOT NULL,
    proverb_persian TEXT NOT NULL,
    proverb_english TEXT,
    literal_meaning TEXT,
    figurative_meaning TEXT,
    usage_context TEXT,
    dialect_code TEXT DEFAULT 'ban',
    category TEXT DEFAULT 'wisdom',
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_proverb_bandari ON bandari_proverbs(proverb_bandari);
CREATE TABLE bandari_dialogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dialogue_title TEXT,
    dialogue_type TEXT,
    scene_description TEXT,
    speaker_a TEXT,
    speaker_b TEXT,
    line_number INTEGER,
    text_bandari TEXT NOT NULL,
    text_persian TEXT NOT NULL,
    text_english TEXT,
    pronunciation_notes TEXT,
    context_notes TEXT,
    emotion_tone TEXT,
    dialect_code TEXT DEFAULT 'ban',
    dialect_variant TEXT DEFAULT 'بندرعباس',
    location_context TEXT,
    is_question BOOLEAN DEFAULT 0,
    is_response BOOLEAN DEFAULT 0,
    related_poi_id TEXT,
    source_reference TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_dialogue_type ON bandari_dialogues(dialogue_type);
CREATE INDEX idx_dialogue_dialect ON bandari_dialogues(dialect_code);
CREATE INDEX idx_dialogue_location ON bandari_dialogues(location_context);
CREATE TABLE bandari_grammar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_category TEXT,
    rule_title TEXT,
    rule_description TEXT,
    example_bandari TEXT,
    example_persian TEXT,
    example_english TEXT,
    dialect_code TEXT DEFAULT 'ban',
    complexity_level TEXT,
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_grammar_category ON bandari_grammar(rule_category);
CREATE TABLE bandari_texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    text_type TEXT,
    author_artist TEXT,
    text_bandari TEXT NOT NULL,
    text_persian TEXT NOT NULL,
    text_english TEXT,
    genre TEXT,
    dialect_code TEXT DEFAULT 'ban',
    dialect_variant TEXT DEFAULT 'بندرعباس',
    year_recorded INTEGER,
    media_url TEXT,
    lyrics_json TEXT,
    source_reference TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_text_type ON bandari_texts(text_type);
CREATE INDEX idx_text_dialect ON bandari_texts(dialect_code);
CREATE TABLE dialect_comparison (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_standard TEXT,
    word_bandari TEXT,
    word_minabi TEXT,
    word_rudani TEXT,
    word_bastaki TEXT,
    word_lengei TEXT,
    word_hormozi TEXT,
    word_qeshmi TEXT,
    word_kishi TEXT,
    word_lari TEXT,
    word_persian TEXT,
    word_english TEXT,
    category TEXT,
    notes TEXT,
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_comparison_standard ON dialect_comparison(word_standard);
CREATE INDEX idx_comparison_category ON dialect_comparison(category);
CREATE TABLE bandari_professional_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term_bandari TEXT NOT NULL,
    term_persian TEXT NOT NULL,
    profession_field TEXT,
    term_definition TEXT,
    usage_example TEXT,
    dialect_code TEXT DEFAULT 'ban',
    dialect_variant TEXT DEFAULT 'بندرعباس',
    is_still_used BOOLEAN DEFAULT 1,
    source_reference TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_prof_term_field ON bandari_professional_terms(profession_field);
CREATE TABLE bandari_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    items_count INTEGER,
    dialect_variant TEXT,
    status TEXT,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE VIRTUAL TABLE bandari_fts USING fts5(
    content,
    content='bandari_dialogues',
    content_rowid='rowid'
)
/* bandari_fts(content) */;
CREATE TABLE 'bandari_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE 'bandari_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE 'bandari_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'bandari_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TRIGGER bandari_dialogues_fts_insert AFTER INSERT ON bandari_dialogues BEGIN
    INSERT INTO bandari_fts(rowid, content) VALUES (new.rowid, new.text_bandari || ' ' || new.text_persian || ' ' || COALESCE(new.text_english, ''));
END;
CREATE TRIGGER bandari_dialogues_fts_delete AFTER DELETE ON bandari_dialogues BEGIN
    INSERT INTO bandari_fts(bandari_fts, rowid, content) VALUES('delete', old.rowid, old.text_bandari || ' ' || old.text_persian || ' ' || COALESCE(old.text_english, ''));
END;
CREATE TRIGGER bandari_dialogues_fts_update AFTER UPDATE ON bandari_dialogues BEGIN
    INSERT INTO bandari_fts(bandari_fts, rowid, content) VALUES('delete', old.rowid, old.text_bandari || ' ' || old.text_persian || ' ' || COALESCE(old.text_english, ''));
    INSERT INTO bandari_fts(rowid, content) VALUES (new.rowid, new.text_bandari || ' ' || new.text_persian || ' ' || COALESCE(new.text_english, ''));
END;
CREATE VIEW v_bandari_rag_corpus AS
SELECT 
    'vocabulary' as source_type,
    id as source_id,
    word_bandari as content_bandari,
    word_standard as content_persian,
    word_english as content_english,
    category,
    dialect_code,
    confidence_score,
    data_quality
FROM bandari_vocabulary
UNION ALL
SELECT 
    'dialogue' as source_type,
    id as source_id,
    text_bandari as content_bandari,
    text_persian as content_persian,
    text_english as content_english,
    dialogue_type as category,
    dialect_code,
    85 as confidence_score,
    'verified' as data_quality
FROM bandari_dialogues
UNION ALL
SELECT 
    'phrase' as source_type,
    id as source_id,
    phrase_bandari as content_bandari,
    phrase_persian as content_persian,
    phrase_english as content_english,
    category,
    dialect_code,
    confidence_score,
    'verified' as data_quality
FROM bandari_phrases
UNION ALL
SELECT 
    'proverb' as source_type,
    id as source_id,
    proverb_bandari as content_bandari,
    proverb_persian as content_persian,
    proverb_english as content_english,
    category,
    dialect_code,
    80 as confidence_score,
    'verified' as data_quality
FROM bandari_proverbs
/* v_bandari_rag_corpus(source_type,source_id,content_bandari,content_persian,content_english,category,dialect_code,confidence_score,data_quality) */;
CREATE VIEW v_bandari_stats AS
SELECT 
    (SELECT COUNT(*) FROM bandari_vocabulary) as total_vocabulary,
    (SELECT COUNT(*) FROM bandari_dialogues) as total_dialogues,
    (SELECT COUNT(*) FROM bandari_phrases) as total_phrases,
    (SELECT COUNT(*) FROM bandari_proverbs) as total_proverbs,
    (SELECT COUNT(*) FROM bandari_texts) as total_texts,
    (SELECT COUNT(*) FROM bandari_grammar) as total_grammar_rules,
    (SELECT COUNT(*) FROM dialect_comparison) as total_comparisons,
    (SELECT COUNT(*) FROM bandari_professional_terms) as total_professional_terms,
    (SELECT COUNT(DISTINCT category) FROM bandari_vocabulary) as categories_count,
    (SELECT COUNT(DISTINCT dialect_code) FROM bandari_vocabulary) as dialects_count
/* v_bandari_stats(total_vocabulary,total_dialogues,total_phrases,total_proverbs,total_texts,total_grammar_rules,total_comparisons,total_professional_terms,categories_count,dialects_count) */;
CREATE TABLE transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    transport_type TEXT,
    operator TEXT,
    network TEXT,
    lat REAL,
    lon REAL,
    city TEXT,
    district TEXT,
    route_number TEXT,
    schedule TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
