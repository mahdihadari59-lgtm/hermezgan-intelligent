from src.experts.base import Expert
from src.knowledge.db_connector import db

class AutoExpert(Expert):
    expert_id = "auto"
    expert_name = "متخصص خودرو"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name == "auto"

    def process(self, query: str, entities: dict) -> list:
        city = entities.get("city", "")
        return db.query(
            "SELECT * FROM fuel_stations WHERE city LIKE ? LIMIT 10",
            (f"%{city}%",)
        )
