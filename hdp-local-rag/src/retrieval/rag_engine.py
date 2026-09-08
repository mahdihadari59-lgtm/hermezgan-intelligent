from typing import List, Dict, Any
from src.knowledge.db_connector import db
from src.core.query_planner import PlanStep

class RagEngine:
    def retrieve(self, query: str, intent_name: str, steps: List[PlanStep]) -> List[Dict[str, Any]]:
        results = []
        for step in steps:
            if step.table == "pois":
                results += db.search_pois(query, limit=5)
            elif step.table == "tourism_poi":
                results += db.search_tourism(query, limit=5)
            elif step.table == "markets":
                results += db.search_business(query, limit=5)
            elif step.table == "roads":
                results += db.query("SELECT * FROM roads WHERE name_fa LIKE ? LIMIT 5", (f"%{query}%",))
            elif step.table == "traffic_data":
                results += db.query("SELECT * FROM traffic_data LIMIT 5")
            elif step.table == "restaurants":
                results += db.query("SELECT * FROM restaurants WHERE city LIKE ? LIMIT 5", (f"%{step.filters.get('city','')}%",))
            elif step.table == "hotels":
                results += db.query("SELECT * FROM hotels WHERE city LIKE ? LIMIT 5", (f"%{step.filters.get('city','')}%",))
            elif step.table == "fuel_stations":
                results += db.query("SELECT * FROM fuel_stations WHERE city LIKE ? LIMIT 5", (f"%{step.filters.get('city','')}%",))
        return results
