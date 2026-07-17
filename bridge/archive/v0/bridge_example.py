#!/usr/bin/env python3
"""
geo/bridge_example.py — runnable demo of DatabaseBridge against real geo.db.

This is NOT wired into server.py yet. Point 3 of the integration plan
("تغییر APIها") needs the real column/table names in hdp_v2.db's
knowledge_relations / knowledge tables to write correctly -- this example
uses the schema recalled from earlier HDP sessions (knowledge_relations:
source_entity, target_entity, relation_type, weight). Confirm against the
real file before adapting api/*.py to use the bridge.

Usage:
    python3 bridge_example.py --geo-db ../db/geo.db --knowledge-db /path/to/hdp_v2.db
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_bridge import DatabaseBridge

def main(geo_db: str, knowledge_db: str) -> None:
    with DatabaseBridge(geo_db, knowledge_db) as bridge:
        print("Attached schemas:")
        for s in bridge.list_schemas():
            print(f"  {s['name']:12s} {s['file']}")

        print("\nTables in geo.db (main):", ", ".join(bridge.tables_in("main")))
        print("Tables in knowledge:", ", ".join(bridge.tables_in("knowledge")))

        print("\nExample: geo.db hospitals that also appear as entities in the knowledge graph")
        try:
            rows = bridge.query(
                """
                SELECT h.name AS hospital_name, h.lat, h.lng, r.target_entity, r.weight
                FROM hospitals h
                JOIN knowledge.knowledge_relations r
                  ON r.source_entity = 'hospital:' || h.name
                ORDER BY r.weight DESC
                LIMIT 20
                """
            )
            for r in rows:
                print(f"  {r['hospital_name']} <-> {r['target_entity']}  (weight={r['weight']})")
            if not rows:
                print("  (no matches -- expected until hospital names in geo.db and entity")
                print("   strings in knowledge_relations use the same naming convention)")
        except Exception as e:
            print(f"  Query failed -- likely a schema mismatch, adjust to match the real "
                  f"hdp_v2.db columns: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo the geo.db <-> knowledge engine bridge")
    parser.add_argument("--geo-db", default="../db/geo.db")
    parser.add_argument("--knowledge-db", required=True)
    args = parser.parse_args()
    main(args.geo_db, args.knowledge_db)
