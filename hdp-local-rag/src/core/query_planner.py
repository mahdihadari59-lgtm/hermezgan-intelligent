from dataclasses import dataclass
from typing import List, Dict
from src.core.intent_router import Intent

@dataclass
class PlanStep:
    action: str
    table: str
    filters: Dict[str, str]

class QueryPlanner:
    def create_plan(self, intent: Intent, entities: Dict[str, str]) -> List[PlanStep]:
        steps = []
        city = entities.get("city", "")

        if intent.name == "tourism":
            steps.append(PlanStep("search", "tourism_poi", {"city": city, "category": "attraction"}))
            steps.append(PlanStep("search", "restaurants", {"city": city}))
        elif intent.name == "business":
            steps.append(PlanStep("search", "markets", {"city": city}))
            steps.append(PlanStep("search", "hotels", {"city": city}))
        elif intent.name == "routing":
            steps.append(PlanStep("search", "roads", {"city": city}))
            steps.append(PlanStep("search", "cameras_atlas", {"city": city}))
        elif intent.name == "traffic":
            steps.append(PlanStep("search", "traffic_data", {"city": city}))
            steps.append(PlanStep("search", "accident_hotspots", {"city": city}))
        elif intent.name == "auto":
            steps.append(PlanStep("search", "fuel_stations", {"city": city}))
        else:
            steps.append(PlanStep("search", "pois", {"city": city}))

        return steps
