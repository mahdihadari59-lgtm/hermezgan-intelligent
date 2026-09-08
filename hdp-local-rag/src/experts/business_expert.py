from src.experts.base import Expert
from src.knowledge.db_connector import db

class BusinessExpert(Expert):
    expert_id = "business"
    expert_name = "متخصص کسب‌وکار"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name in ["business", "local"]

    def process(self, query: str, entities: dict) -> list:
        city = entities.get("city", "")
        if city:
            return db.query(
                "SELECT * FROM markets WHERE city LIKE ? LIMIT 10",
                (f"%{city}%",)
            )
        return db.search_business(query, limit=10)
