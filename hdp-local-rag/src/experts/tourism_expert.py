from src.experts.base import Expert
from src.knowledge.db_connector import db

class TourismExpert(Expert):
    expert_id = "tourism"
    expert_name = "متخصص گردشگری"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["tourism", "local"]

    def process(self, query: str, entities: dict) -> list:
        city = entities.get("city", "")
        if city:
            return db.query(
                "SELECT * FROM tourism_poi WHERE city LIKE ? LIMIT 10",
                (f"%{city}%",)
            )
        return db.search_tourism(query, limit=10)
