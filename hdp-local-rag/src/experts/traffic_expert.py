from src.experts.base import Expert
from src.knowledge.db_connector import db

class TrafficExpert(Expert):
    expert_id = "traffic"
    expert_name = "متخصص ترافیک"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name == "traffic"

    def process(self, query: str, entities: dict) -> list:
        city = entities.get("city", "")
        return db.query(
            "SELECT * FROM traffic_data WHERE city LIKE ? ORDER BY timestamp DESC LIMIT 10",
            (f"%{city}%",)
        )
