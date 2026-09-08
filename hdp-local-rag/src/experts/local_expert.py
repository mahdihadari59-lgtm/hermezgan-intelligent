from src.experts.base import Expert
from src.knowledge.db_connector import db
from typing import Dict, Any, List

class LocalExpert(Expert):
    expert_id = "local"
    expert_name = "متخصص محلی"

    def can_handle(self, intent_name: str) -> bool:
        return True

    def process(self, query: str, entities: Dict[str, str]) -> List[Dict[str, Any]]:
        city = entities.get("city", "")
        results = []
        if city:
            results += db.query("SELECT * FROM cities WHERE name_fa LIKE ?", (f"%{city}%",))
            results += db.query("SELECT * FROM neighborhoods WHERE city LIKE ?", (f"%{city}%",))
        results += db.search_pois(query, limit=5)
        return results
