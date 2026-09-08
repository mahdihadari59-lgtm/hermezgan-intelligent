from src.experts.base import Expert
from src.knowledge.db_connector import db

class RoutingExpert(Expert):
    expert_id = "routing"
    expert_name = "متخصص مسیریابی"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["routing", "traffic", "auto"]

    def process(self, query: str, entities: dict) -> list:
        city = entities.get("city", "")
        return db.query(
            "SELECT * FROM roads WHERE name_fa LIKE ? OR city LIKE ? LIMIT 10",
            (f"%{query}%", f"%{city}%")
        )
