# 📋 گزارش ناهماهنگی نام ستون‌ها

تعداد کل جدول‌ها: **142**

## بخش ۱ — ناهماهنگی به تفکیک مفهوم

### مفهوم: `latitude`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `lat` در **48** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - accident_hotspots, backup_accident_hotspots, backup_traffic_data, backup_transport, banks, cafes, cameras_atlas, cities, cultural_sites, education, education_geo, educational_centers, fuel_stations, geo_pois_master, geo_reference_cameras_master, ... و 33 جدول دیگر
- `latitude` در **4** جدول
  - city_info, documents, tourism_poi, web_content

### مفهوم: `longitude`
⚠️ **ناهماهنگ** — 3 نام مختلف برای این مفهوم استفاده شده:

- `lon` در **45** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - accident_hotspots, backup_accident_hotspots, backup_traffic_data, backup_transport, banks, cafes, cameras_atlas, cities, cultural_sites, education, education_geo, educational_centers, fuel_stations, healthcare, healthcare_geo, ... و 30 جدول دیگر
- `longitude` در **4** جدول
  - city_info, documents, tourism_poi, web_content
- `lng` در **3** جدول
  - geo_pois_master, geo_reference_cameras_master, geo_traffic_master

### مفهوم: `name`
⚠️ **ناهماهنگ** — 4 نام مختلف برای این مفهوم استفاده شده:

- `name` در **47** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - accident_hotspots, backup_accident_hotspots, backup_transport, banks, bridges, cafes, cameras_atlas, cameras_info, cities, education, education_geo, educational_centers, fuel_stations, geo_pois_master, geo_reference_cameras_master, ... و 32 جدول دیگر
- `name_fa` در **29** جدول
  - backup_transport, boutiques, cities, cultural_sites, dialect_info_master, education, education_geo, graph_entities, healthcare, healthcare_geo, justice_sites, markets, markets_geo, music_schools, natural_attractions, ... و 14 جدول دیگر
- `title` در **8** جدول
  - backup_traffic_info, bandari_texts_master, documents, knowledge, knowledge_sources, traffic_info, web_content, web_content_fts
- `label` در **1** جدول
  - graph_nodes_master

### مفهوم: `name_en`
✅ همگی از یک نام استفاده می‌کنند:

- `name_en` در **6** جدول
  - dialect_info_master, graph_entities, tourism_activities, tourism_events, tourism_food, tourism_poi

### مفهوم: `phone`
✅ همگی از یک نام استفاده می‌کنند:

- `phone` در **17** جدول
  - banks, documents, education, geo_pois_master, healthcare, hotels, industries, justice_sites, major_infrastructure, markets, offices, pharmacies, pois, restaurants, therapy_clinics, ... و 2 جدول دیگر

### مفهوم: `address`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `address` در **6** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - banks, documents, pharmacies, pois, restaurants, web_content
- `location` در **4** جدول
  - cameras_info, hotspots_info, shopping_centers, traffic_devices

### مفهوم: `category`
⚠️ **ناهماهنگ** — 3 نام مختلف برای این مفهوم استفاده شده:

- `category` در **18** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - backup_traffic_info, bandari_phrases_master, bandari_proverbs_master, bandari_vocabulary_master, collection_log, dialect_comparison_master, documents, geo_pois_master, graph_entities, graph_knowledge_entities, knowledge, spatial_grid, tourism_activities, tourism_food, tourism_poi, ... و 3 جدول دیگر
- `cat` در **2** جدول
  - osm_import_staging, pois
- `type` در **1** جدول
  - graph_knowledge_entities

### مفهوم: `description`
⚠️ **ناهماهنگ** — 3 نام مختلف برای این مفهوم استفاده شده:

- `description` در **7** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - city_statistics, geo_pois_master, graph_entities_master, graph_knowledge_entities, graph_relation_types_master, relation_types, web_content
- `details` در **2** جدول
  - cameras_info, major_infrastructure
- `definition` در **1** جدول
  - bandari_vocabulary_master

### مفهوم: `created_at`
⚠️ **ناهماهنگ** — 3 نام مختلف برای این مفهوم استفاده شده:

- `created_at` در **63** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - accident_hotspots, alternative_routes, backup_accident_hotspots, backup_alternative_routes, backup_routes, backup_traffic_info, bandari_grammar_master, bandari_phrases_master, bandari_proverbs_master, bandari_vocabulary_master, banks, bridges, cafes, cameras_atlas, cameras_info, ... و 48 جدول دیگر
- `collected_at` در **26** جدول
  - backup_transport, bandari_dialogues_master, bandari_professional_terms_master, bandari_texts_master, boutiques, cities, cultural_sites, education, education_geo, healthcare, healthcare_geo, justice_sites, markets, markets_geo, music_schools, ... و 11 جدول دیگر
- `timestamp` در **3** جدول
  - backup_traffic_data, collection_log, traffic_data

### مفهوم: `city`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `city` در **35** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - backup_traffic_info, backup_transport, boutiques, city_history, city_statistics, cultural_sites, education, education_geo, healthcare, healthcare_geo, industries, justice_sites, knowledge, markets, markets_geo, ... و 20 جدول دیگر
- `city_name` در **1** جدول
  - city_info

### مفهوم: `district`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `district` در **21** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - backup_transport, cultural_sites, documents, education, education_geo, healthcare, healthcare_geo, justice_sites, markets, markets_geo, natural_attractions, neighborhoods_detailed, offices, osm_import_staging, parks, ... و 6 جدول دیگر
- `neighborhood` در **3** جدول
  - geo_pois_master, neighborhoods_v3, urban_areas

### مفهوم: `source`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `source` در **15** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - accident_hotspots, backup_accident_hotspots, backup_traffic_data, city_statistics, graph_edges_rag, industries, knowledge, major_infrastructure, piers, realtime_traffic, tourism_poi, tourism_relations, traffic_data, traffic_devices, universities
- `source_reference` در **10** جدول
  - bandari_dialogues_master, bandari_grammar_master, bandari_phrases_master, bandari_professional_terms_master, bandari_proverbs_master, bandari_texts_master, bandari_vocabulary_master, dialect_comparison_master, graph_entity_attributes_master, graph_relations_master

### مفهوم: `confidence`
⚠️ **ناهماهنگ** — 2 نام مختلف برای این مفهوم استفاده شده:

- `confidence` در **11** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - graph_edges_rag, graph_knowledge_relations, graph_relations_master, industries, knowledge, major_infrastructure, tourism_activities, tourism_events, tourism_food, tourism_poi, tourism_relations
- `confidence_score` در **2** جدول
  - bandari_phrases_master, bandari_vocabulary_master

### مفهوم: `id_ref`
⚠️ **ناهماهنگ** — 3 نام مختلف برای این مفهوم استفاده شده:

- `entity_id` در **3** جدول ← 🏆 پیشنهاد به‌عنوان نام استاندارد
  - graph_entity_aliases_master, graph_entity_attributes_master, graph_nodes_master
- `related_poi_id` در **2** جدول
  - bandari_dialogues_master, bandari_vocabulary_master
- `poi_id` در **2** جدول
  - poi_descriptions, poi_descriptions_fts

## بخش ۲ — جدول‌هایی با مختصات ناقص (فقط lat یا فقط lon/lng)


## بخش ۳ — جدول‌ها و تعداد ستون‌های ناشناخته (خارج از گروه‌های تعریف‌شده بالا)

این بخش صرفاً اطلاعاتی است — یعنی ستون‌هایی که مخصوص همان جدول‌اند (طبیعی است).

- `city_info` (30 ستون کل): old_names, english_name, is_capital, province, population_2015, population_2024, population_2026, metro_population_2026, growth_rate, area_km2, ... +16
- `documents` (30 ستون کل): source_id, url, final_url, canonical_url, business_name, meta_description, og_title, og_description, language, text_summary, ... +12
- `tourism_poi` (29 ستون کل): name_aliases, province, subcategory, poi_type, description_fa, description_en, geometry_type, coordinate_source, best_time, activities, ... +8
- `geo_pois_master` (26 ستون کل): tags_json, tenant_uuid, updated_at, branch_code, working_hours, bank_services, has_atm, has_parking, has_exchange, website, ... +8
- `bandari_vocabulary_master` (22 ستون کل): word_standard, word_bandari, word_english, phonetic_ipa, part_of_speech, subcategory, etymology, cultural_note, example_bandari, example_persian, ... +5
- `bandari_dialogues_master` (21 ستون کل): dialogue_title, dialogue_type, scene_description, speaker_a, speaker_b, line_number, text_bandari, text_persian, text_english, pronunciation_notes, ... +7
- `web_content` (19 ستون کل): url, content, mobile, website, postal_code, photos, word_count, content_hash, fetched_at, business_name
- `dialect_comparison_master` (17 ستون کل): word_standard, word_bandari, word_minabi, word_rudani, word_bastaki, word_lengei, word_hormozi, word_qeshmi, word_kishi, word_lari, ... +3
- `knowledge` (17 ستون کل): content, subcategory, province, source_url, source_type, data_period, verification_status, keywords, priority, updated_at
- `roads` (17 ستون کل): osm_id, road_type, surface, lanes, oneway, maxspeed, lit, geom_type, geometry_json
- `tourism_food` (17 ستون کل): counties, description_fa, ingredients, cooking_method, serving_style, local_names, dialect_names, allergens, vegetarian, seafood, ... +1
- `accident_hotspots` (16 ستون کل): accident_type, severity, cause, suggestion, rank, accidents, fatalities, injuries, year, last_updated
- `backup_accident_hotspots` (16 ستون کل): accident_type, severity, cause, suggestion, rank, accidents, fatalities, injuries, year, last_updated
- `offices` (16 ستون کل): osm_id, office_type, organization, fax, email, website, opening_hours
- `bandari_texts_master` (15 ستون کل): text_type, author_artist, text_bandari, text_persian, text_english, genre, dialect_code, dialect_variant, year_recorded, media_url, ... +1
- `education` (15 ستون کل): osm_id, edu_type, level, operator, website, opening_hours
- `healthcare` (15 ستون کل): osm_id, healthcare_type, specialities, emergency, website, opening_hours
- `markets` (15 ستون کل): osm_id, shop_type, brand, opening_hours, website, sub_category
- `backup_transport` (14 ستون کل): osm_id, transport_type, operator, network, route, schedule
- `transport` (14 ستون کل): osm_id, transport_type, operator, network, route, schedule
- `industries` (12 ستون کل): activity_type, employees_approx, location_note
- `backup_routes` (11 ستون کل): origin, destination, route, normal_time, peak_time, distance, condition, safety_score, hotspot_count
- `bandari_grammar_master` (11 ستون کل): rule_category, rule_title, rule_description, example_bandari, example_persian, example_english, dialect_code, complexity_level
- `bandari_professional_terms_master` (11 ستون کل): term_bandari, term_persian, profession_field, term_definition, usage_example, dialect_code, dialect_variant, is_still_used
- `bandari_proverbs_master` (11 ستون کل): proverb_bandari, proverb_persian, proverb_english, literal_meaning, figurative_meaning, usage_context, dialect_code
- `major_infrastructure` (11 ستون کل): infra_type, status
- `pois` (11 ستون کل): website
- `route_distances` (11 ستون کل): origin_id, destination_id, origin_name, destination_name, distance_km, duration_min, traffic_level, route_geometry, updated_at
- `routes` (11 ستون کل): origin, destination, route, normal_time, peak_time, distance, condition, safety_score, hotspot_count
- `tourism_activities` (11 ستون کل): counties, equipment, best_season, difficulty, description_fa
- `universities` (11 ستون کل): university_type, main_fields, student_count_approx
- `bandari_phrases_master` (10 ستون کل): phrase_bandari, phrase_persian, phrase_english, context, dialect_code
- `education_geo` (10 ستون کل): osm_id, education_type
- `healthcare_geo` (10 ستون کل): osm_id, healthcare_type
- `hotspots_info` (10 ستون کل): severity, accidents, fatalities, injuries, accident_type, cause
- `markets_geo` (10 ستون کل): osm_id, shop_type
- `neighborhoods` (10 ستون کل): osm_id, place_type, population
- `piers` (10 ستون کل): pier_type, location_city, distance_km_to_center, travel_time_note
- `rag_routing` (10 ستون کل): source_table, record_id, content, embedding, embedding_type, metadata_json
- `traffic_devices` (10 ستون کل): device_id, device_type, road_name, status
- `backup_traffic_data` (9 ستون کل): road_name, road_osm_id, speed_kmh, congestion_level
- `cities` (9 ستون کل): osm_id, place_type, population
- `graph_edges_rag` (9 ستون کل): source_id, target_id, relation_type, relation_category, weight
- `graph_entities` (9 ستون کل): entity_type, description_fa, metadata_json, keywords
- `graph_relations_master` (9 ستون کل): source_entity_id, target_entity_id, relation_type_id, weight, metadata
- `justice_sites` (9 ستون کل): site_type
- `neighborhoods_detailed` (9 ستون کل): row_number, old_name, urban_zone, texture_type
- `osm_import_staging` (9 ستون کل): osm_node_id, imported_at, routed
- `shopping_centers` (9 ستون کل): center_type, hours, features
- `spatial_grid` (9 ستون کل): table_name, record_id, grid_lat, grid_lon
- `tourism_events` (9 ستون کل): county, event_type, month, description_fa
- `traffic_data` (9 ستون کل): road_name, road_osm_id, speed_kmh, congestion_level
- `urban_areas` (9 ستون کل): region, region_name, area_type, usage
- `urban_zones` (9 ستون کل): zone_name, local_name, main_neighborhoods, population_estimate, characteristics, infrastructure_status
- `user_routing_history` (9 ستون کل): session_id, origin, destination, selected_route_id, actual_distance_km, actual_duration_min, request_time, user_ip
- `banks` (8 ستون کل): bank_type
- `cameras_atlas` (8 ستون کل): camera_type, status, priority
- `cultural_sites` (8 ستون کل): site_type
- `dialect_info_master` (8 ستون کل): code, region, population_estimate, is_verified, word_count, notes
- `geo_reference_cameras_master` (8 ستون کل): code, status, types_json, updated_at
- `geo_roads_master` (8 ستون کل): min_lat, max_lat, min_lng, max_lng, road_class, updated_at
- `geo_traffic_master` (8 ستون کل): level, speed_kmh, delay_min, updated_at
- `graph_knowledge_entities` (8 ستون کل): metadata, embedding
- `hotels` (8 ستون کل): stars, capacity
- `knowledge_sources` (8 ستون کل): publisher, url, source_type, publication_date, accessed_at, reliability_level
- `natural_attractions` (8 ستون کل): attraction_type
- `parks` (8 ستون کل): park_type
- `pharmacies` (8 ستون کل): pharmacy_type
- `rag_embeddings` (8 ستون کل): table_name, record_id, content, embedding, embedding_type, metadata_json
- `realtime_traffic` (8 ستون کل): road_id, road_name, traffic_level, speed_kmh, delay_minutes, last_updated
- `religious_sites` (8 ستون کل): site_type
- `restaurants` (8 ستون کل): restaurant_type
- `schools` (8 ستون کل): school_type, gender
- `tourism_relations` (8 ستون کل): source_id, relation, target_id, weight
- `cameras_info` (7 ستون کل): camera_type, status
- `city_history` (7 ستون کل): era, year, event, population_estimate
- `city_statistics` (7 ستون کل): indicator, value
- `graph_entities_master` (7 ستون کل): entity_type, source_id, updated_at
- `graph_entity_attributes_master` (7 ستون کل): attribute_key, attribute_value, attribute_type
- `graph_knowledge_relations` (7 ستون کل): source_id, target_id, relation_type, weight
- `graph_relation_types_master` (7 ستون کل): code, label_fa, label_en, is_bidirectional
- `medical_centers` (7 ستون کل): center_type, beds
- `parking_lots` (7 ستون کل): capacity, lot_type
- `reference_points` (7 ستون کل): region, point_type
- `backup_traffic_info` (6 ستون کل): content
- `cafes` (6 ستون کل): cafe_type
- `collection_log` (6 ستون کل): items_count, status, message
- `educational_centers` (6 ستون کل): edu_type
- `fuel_stations` (6 ستون کل): fuel_type
- `graph_edges_master` (6 ستون کل): source_node_id, target_node_id, relation_type, weight, metadata_json
- `poi_graph_edges` (6 ستون کل): source_poi_id, target_poi_id, relation_type, weight
- `souvenir_shops` (6 ستون کل): shop_type
- `therapy_clinics` (6 ستون کل): clinic_type
- `tourist_areas` (6 ستون کل): area_type
- `traffic_info` (6 ستون کل): content
- `alternative_routes` (5 ستون کل): main_route, alternative_route, reason
- `backup_alternative_routes` (5 ستون کل): main_route, alternative_route, reason
- `boutiques` (5 ستون کل): boutique_type
- `graph_entity_aliases_master` (5 ستون کل): alias_name, language, is_primary
- `graph_nodes_master` (5 ستون کل): node_type, metadata_json
- `master_sources` (5 ستون کل): source_name, source_path, source_role, imported_at
- `neighborhoods_v3` (5 ستون کل): region, feature
- `poi_descriptions` (5 ستون کل): content, source_url, source_id
- `rtree_education` (5 ستون کل): min_lat, max_lat, min_lon, max_lon
- `rtree_healthcare` (5 ستون کل): min_lat, max_lat, min_lon, max_lon
- `rtree_markets` (5 ستون کل): min_lat, max_lat, min_lon, max_lon
- `rtree_roads` (5 ستون کل): minLat, maxLat, minLon, maxLon
- `rtree_transport` (5 ستون کل): min_lat, max_lat, min_lon, max_lon
- `web_content_fts` (5 ستون کل): content, url
- `bridges` (4 ستون کل): role
- `entity_types` (4 ستون کل): code, label_fa, parent_category
- `private_schools` (4 ستون کل): school_type
- `public_schools` (4 ستون کل): school_type
- `relation_types` (4 ستون کل): code, label_fa
- `squares` (4 ستون کل): role
- `technical_schools` (4 ستون کل): school_type
- `poi_descriptions_fts_idx` (3 ستون کل): segid, term, pgno
- `sources` (3 ستون کل): site_name, url
- `web_content_fts_idx` (3 ستون کل): segid, term, pgno
- `poi_descriptions_fts` (2 ستون کل): content
- `poi_descriptions_fts_config` (2 ستون کل): k, v
- `poi_descriptions_fts_data` (2 ستون کل): block
- `poi_descriptions_fts_docsize` (2 ستون کل): sz
- `rtree_education_node` (2 ستون کل): nodeno, data
- `rtree_education_parent` (2 ستون کل): nodeno, parentnode
- `rtree_education_rowid` (2 ستون کل): rowid, nodeno
- `rtree_healthcare_node` (2 ستون کل): nodeno, data
- `rtree_healthcare_parent` (2 ستون کل): nodeno, parentnode
- `rtree_healthcare_rowid` (2 ستون کل): rowid, nodeno
- `rtree_markets_node` (2 ستون کل): nodeno, data
- `rtree_markets_parent` (2 ستون کل): nodeno, parentnode
- `rtree_markets_rowid` (2 ستون کل): rowid, nodeno
- `rtree_roads_node` (2 ستون کل): nodeno, data
- `rtree_roads_parent` (2 ستون کل): nodeno, parentnode
- `rtree_roads_rowid` (2 ستون کل): rowid, nodeno
- `rtree_transport_node` (2 ستون کل): nodeno, data
- `rtree_transport_parent` (2 ستون کل): nodeno, parentnode
- `rtree_transport_rowid` (2 ستون کل): rowid, nodeno
- `web_content_fts_config` (2 ستون کل): k, v
- `web_content_fts_data` (2 ستون کل): block
- `web_content_fts_docsize` (2 ستون کل): sz