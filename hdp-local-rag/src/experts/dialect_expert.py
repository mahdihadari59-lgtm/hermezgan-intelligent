from src.experts.base import Expert
from src.knowledge.db_connector import db

class DialectExpert(Expert):
    expert_id = "dialect"
    expert_name = "متخصص گویش محلی"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name == "dialect"

    def process(self, query: str, entities: dict) -> list:
        return db.query(
            "SELECT * FROM bandari_vocabulary_master WHERE word LIKE ? OR meaning LIKE ? LIMIT 10",
            (f"%{query}%", f"%{query}%")
        )
