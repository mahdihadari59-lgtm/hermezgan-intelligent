from typing import List, Dict
from dataclasses import dataclass
from src.core.intent_router import Intent

@dataclass
class ExpertPlan:
    primary: str
    supporting: List[str]
    strategy: str

class ExpertSelector:
    EXPERT_MAP = {
        "routing": ["routing", "local"],
        "traffic": ["traffic", "routing"],
        "tourism": ["tourism", "local", "business"],
        "business": ["business", "local"],
        "auto": ["auto", "routing"],
        "legal": ["legal", "local"],
        "dialect": ["dialect", "local"],
        "local": ["local"],
        "general": ["local", "tourism", "business"],
    }

    def select(self, intent: Intent) -> ExpertPlan:
        experts = self.EXPERT_MAP.get(intent.name, ["local"])
        primary = experts[0]
        supporting = experts[1:] if len(experts) > 1 else []
        strategy = "PARALLEL" if len(experts) > 1 else "SINGLE"
        return ExpertPlan(primary=primary, supporting=supporting, strategy=strategy)
