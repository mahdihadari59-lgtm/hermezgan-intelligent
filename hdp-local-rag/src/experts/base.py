from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Expert(ABC):
    expert_id: str = ""
    expert_name: str = ""

    @abstractmethod
    def can_handle(self, intent_name: str) -> bool:
        pass

    @abstractmethod
    def process(self, query: str, entities: Dict[str, str]) -> List[Dict[str, Any]]:
        pass
