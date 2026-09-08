from src.experts.base import Expert
from src.knowledge.db_connector import db

class LegalExpert(Expert):
    expert_id = "legal"
    expert_name = "متخصص حقوقی"

    def can_handle(self, intent_name: str) -> bool:
        return intent_name == "legal"

    def process(self, query: str, entities: dict) -> list:
        return db.query(
            "SELECT * FROM knowledge WHERE category='legal' LIMIT 10"
        )
