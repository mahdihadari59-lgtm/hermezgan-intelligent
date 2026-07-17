from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

GEO_DB = PROJECT_ROOT / "geo.db"

HDP_CANDIDATES = [
    Path.home() / "ai-system" / "hdp_x1" / "data" / "hdp_v2.db",
    Path.home() / "ai-system" / "hdp_x1" / "development" / "data" / "hdp_v2.db",
    Path.home() / "ai-system" / "hdp_x1" / "hdp_v2.db",
]

HDP_DB = next((p for p in HDP_CANDIDATES if p.exists()), HDP_CANDIDATES[0])

KNOWLEDGE_DB = HDP_DB
