HDP VERIFIED THREE-SOURCE IMPORT
================================

Files:
- bandarabbas_atlas_v3_roads_traffic_ports.json
- bandarabbas_deep_research_atlas_v2.json
- knowledge_index_2.json
- scripts/import_verified_sources.py

Safety:
- Refuses to run unless graph_edges is empty.
- Does not modify knowledge_links.
- Creates a timestamped DB backup before import.
- Stores all three source JSON documents verbatim in atlas_master.
- Imports neighborhoods, roads, facilities/commercial zones/ports into the matching atlas tables.
- Creates only explicit, source-backed graph edges (no category full-mesh, no traffic_group/medical_group/food_group generation).
- Records SHA-256 provenance in verified_import_audit.
