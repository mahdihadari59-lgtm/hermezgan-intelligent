from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Sequence

@dataclass
class QueryPlan:
    intent: str
    expert: str
    priority: int
    search_modes: List[str]
    table_targets: List[str]
    needs_graph: bool = False
    needs_embedding: bool = False
    needs_fts: bool = True
    needs_sql: bool = True
    reason: str = ""

class QueryPlannerService:
    """
    Stage 6/7 planner:
    - decides intent
    - maps likely tables
    - chooses retrieval modes
    """

    ROUTE = {
        "route": {
            "expert": "route",
            "tables": [
                "query_routes", "roads", "roads", "knowledge_links",
                "knowledge_relations", "graph_paths", "graph_edges",
                "knowledge_graph", "knowledge_search", "knowledge"
            ],
            "modes": ["fts", "graph", "sql", "embedding"],
            "priority": 1,
            "reason": "routing / distance / path query",
        },
        "traffic": {
            "expert": "traffic",
            "tables": [
                "traffic_cameras", "traffic_blackspots", "traffic_accidents",
                "traffic_cameras_fts", "traffic_blackspots_fts",
                "knowledge", "knowledge_fts", "unified_search", "search_index"
            ],
            "modes": ["fts", "sql", "graph", "embedding"],
            "priority": 1,
            "reason": "traffic / congestion / camera / accident query",
        },
        "weather": {
            "expert": "weather",
            "tables": [
                "knowledge", "knowledge_fts", "unified_search", "search_index",
                "places", "cities", "counties"
            ],
            "modes": ["fts", "sql", "embedding"],
            "priority": 2,
            "reason": "weather / climate query",
        },
        "tourist": {
            "expert": "tourism",
            "tables": [
                "attractions", "places", "hotels", "restaurants", "cafes",
                "shopping_centers", "cultural_items", "proverbs",
                "knowledge", "knowledge_fts", "unified_search"
            ],
            "modes": ["fts", "sql", "embedding", "graph"],
            "priority": 2,
            "reason": "tourism / attraction / place query",
        },
        "medical": {
            "expert": "medical",
            "tables": [
                "hospitals", "clinics", "pharmacies", "medical_entities",
                "medical_relations", "knowledge", "knowledge_fts", "unified_search"
            ],
            "modes": ["fts", "sql", "embedding"],
            "priority": 1,
            "reason": "medical / health query",
        },
        "emergency": {
            "expert": "emergency",
            "tables": [
                "police_services", "police_stations", "hospitals",
                "traffic_accidents", "knowledge", "knowledge_fts", "unified_search"
            ],
            "modes": ["fts", "sql", "graph", "embedding"],
            "priority": 1,
            "reason": "emergency / accident / rescue query",
        },
        "transport": {
            "expert": "transport",
            "tables": [
                "fuel_stations", "businesses", "universities", "government_offices",
                "neighborhoods", "neighborhood_links", "knowledge", "knowledge_fts"
            ],
            "modes": ["fts", "sql", "embedding"],
            "priority": 2,
            "reason": "transport / service query",
        },
        "general": {
            "expert": "general",
            "tables": [
                "knowledge", "knowledge_fts", "knowledge_embeddings", "knowledge_graph",
                "graph_nodes", "graph_edges", "semantic_relations",
                "unified_search", "search_index", "search_keywords",
                "response_templates", "query_routes", "intent_mapping"
            ],
            "modes": ["fts", "graph", "sql", "embedding"],
            "priority": 5,
            "reason": "general knowledge query",
        },
    }

    def detect_intent(self, text: str) -> str:
        t = (text or "").lower()
        rules = {
            "route": ["راه", "مسیر", "چطور برم", "چگونه بروم", "فاصله", "کجاست", "مسافت"],
            "traffic": ["ترافیک", "شلوغ", "بسته", "قفل", "ازدحام", "راه بند", "تصادف", "دوربین"],
            "weather": ["هوا", "آب و هوا", "شرجی", "باران", "طوفان", "گرم", "سرد", "دمای"],
            "tourist": ["گردشگری", "جاذبه", "دیدنی", "سفر", "تفریح", "جاهای دیدنی"],
            "medical": ["بیمارستان", "داروخانه", "کلینیک", "درمانگاه", "پزشک", "اورژانس"],
            "emergency": ["امداد", "تصادف", "پنچری", "خرابی", "اورژانس", "آتش", "پلیس", "کمک"],
            "transport": ["اتوبوس", "تاکسی", "شناور", "لندی", "پرواز", "فرودگاه", "بندر", "اسکله"],
        }
        for intent, keywords in rules.items():
            if any(k in t for k in keywords):
                return intent
        return "general"

    def plan(self, text: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        intent = self.detect_intent(text)
        cfg = self.ROUTE.get(intent, self.ROUTE["general"])

        destination = None
        m = re.search(r"(?:به|تا|از)\s+([^\s،.]{2,}(?:\s+[^\s،.]{2,}){0,2})", text or "")
        if m:
            destination = m.group(1).strip()

        plan = QueryPlan(
            intent=intent,
            expert=cfg["expert"],
            priority=cfg["priority"],
            search_modes=list(cfg["modes"]),
            table_targets=list(dict.fromkeys(cfg["tables"])),
            needs_graph=("graph" in cfg["modes"]),
            needs_embedding=("embedding" in cfg["modes"]),
            needs_fts=("fts" in cfg["modes"]),
            needs_sql=("sql" in cfg["modes"]),
            reason=cfg["reason"],
        )

        if destination:
            if "knowledge" not in plan.table_targets:
                plan.table_targets.append("knowledge")

        return {
            **asdict(plan),
            "destination": destination,
            "context": context,
        }

    def summary(self, plan: Dict[str, Any]) -> str:
        return f"{plan.get('intent')}::{plan.get('expert')}::{','.join(plan.get('table_targets') or [])}"
