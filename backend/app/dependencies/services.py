"""
dependencies/services.py

PATCHED. Two real bugs in the original file, found by inspection:

1. `Depends` was used (`db: Session = Depends(get_db)`) but never imported
   from `fastapi` — this is a `NameError` at import time, so the module
   could not even load. Fixed below.

2. `get_chat_service()` called `ChatService(db, redis_client)`, but the
   real `ChatService.__init__` (see services/chat_service.py) only ever
   accepted `(self, db=None)` — a second positional arg raises
   `TypeError: __init__() takes from 1 to 2 positional arguments but 3
   were given` on every single request. The patched ChatService now takes
   `(db=None, gateway=None)`, and `get_chat_service()` below is updated to
   match that real signature — `redis_client` is no longer passed into it
   (nothing in ChatService ever used it; `self._cache` was already a plain
   dict, not Redis-backed).

Also added: `get_copilot_gateway()`, the single entry point that
`chat_service.py` now depends on (per WIRING.md / PATCH_NOTES.md).
Defined BEFORE `get_chat_service()` in this file because FastAPI's
`Depends(get_copilot_gateway)` default is evaluated at function-definition
time — it must already exist in the module namespace by then.

Session-scoping note: KnowledgeProvider/GraphProvider/VectorProvider/
BandariProvider/WeatherProvider and the RAG pipeline built on top of them
do NOT depend on the per-request SQLAlchemy `Session`, so they're built
ONCE as module-level singletons and reused across requests. TrafficExpert/
MedicalExpert/TransportExpert DO depend on `Session`-bound services
(HotspotService, CameraService, ...), so those — and CopilotGateway itself,
since it holds them — are rebuilt per request via `Depends`, cheaply,
reusing the cached singletons underneath.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
import redis

from app.services.chat_service import ChatService
from app.services.nlp_service import NLPService
from app.services.location_service import LocationService
from app.services.camera_service import CameraService
from app.services.hotspot_service import HotspotService
from app.services.analytics_service import AnalyticsService
from app.dependencies.database import get_db, get_redis

# --- Copilot Gateway building blocks -----------------------------------
from app.core.engine.hybrid.knowledge_base import get_knowledge_base
from app.core.engine.hybrid.graph_store import get_graph_store
from app.core.engine.hybrid.vector_store import get_vector_store

from app.providers.bandari_provider import BandariProvider
from app.providers.knowledge_provider import KnowledgeProvider
from app.providers.graph_provider import GraphProvider
from app.providers.vector_provider import VectorProvider
from app.providers.weather_provider import WeatherProvider
from app.pipelines.search_pipeline import SearchPipeline
from app.pipelines.rag_pipeline import RAGPipeline
from app.experts.tourism_expert import TourismExpert
from app.experts.traffic_expert import TrafficExpert
from app.experts.medical_expert import MedicalExpert
from app.experts.transport_expert import TransportExpert
from app.gateway.copilot_gateway import CopilotGateway


# ============================================================
# Location / Camera / Hotspot / Analytics services (unchanged)
# ============================================================

def get_location_service(
    db: Session = Depends(get_db)
) -> LocationService:
    """
    دریافت سرویس مکان‌یابی

    Returns:
        LocationService: سرویس مکان‌یابی
    """
    return LocationService(db)


def get_camera_service(
    db: Session = Depends(get_db)
) -> CameraService:
    """
    دریافت سرویس دوربین‌ها

    Returns:
        CameraService: سرویس دوربین‌ها
    """
    return CameraService(db)


def get_hotspot_service(
    db: Session = Depends(get_db)
) -> HotspotService:
    """
    دریافت سرویس نقاط حادثه‌خیز

    Returns:
        HotspotService: سرویس نقاط حادثه‌خیز
    """
    return HotspotService(db)


def get_analytics_service(
    db: Session = Depends(get_db)
) -> AnalyticsService:
    """
    دریافت سرویس تحلیل داده‌ها

    Returns:
        AnalyticsService: سرویس تحلیل
    """
    return AnalyticsService(db)


def get_nlp_service(
    db: Session = Depends(get_db)
) -> NLPService:
    """
    دریافت سرویس NLP

    Returns:
        NLPService: سرویس پردازش زبان طبیعی
    """
    return NLPService(db)


# ============================================================
# Copilot Gateway
# ============================================================
#
# knowledge/graph/vector/bandari/weather + the RAG pipeline are cheap to
# share across requests (no Session inside them), so they're memoized here
# instead of rebuilt every call.

_rag_pipeline: Optional[RAGPipeline] = None


class _TodoLLMAdapter:
    """
    Placeholder so RAGPipeline is runnable end-to-end before the real LLM
    adapter is wired in. Swap this for Bandari Engine's actual pluggable
    LLM adapter — just make sure it exposes an async
    `generate(prompt: str) -> str`.
    """

    async def generate(self, prompt: str) -> str:
        return "پاسخ‌گویی هوشمند هنوز به LLM واقعی وصل نشده — این یک پاسخ موقت است."


def _get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        bandari = BandariProvider()
        knowledge = KnowledgeProvider(engine=get_knowledge_base())
        graph = GraphProvider(engine=get_graph_store())
        vector = VectorProvider(store=get_vector_store())
        search = SearchPipeline(knowledge=knowledge, graph=graph, vector=vector)
        _rag_pipeline = RAGPipeline(bandari=bandari, search=search, llm=_TodoLLMAdapter())
    return _rag_pipeline


def get_copilot_gateway(
    hotspot_service: HotspotService = Depends(get_hotspot_service),
    camera_service: CameraService = Depends(get_camera_service),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> CopilotGateway:
    """
    نقطه‌ی ورود واحد برای هر چیزی که به knowledge/graph/vector/Bandari/LLM
    نیاز داره. طبق قانونی که در WIRING.md گفته شد، هیچ endpoint دیگه‌ای
    نباید مستقیماً providers/pipelines/experts رو صدا بزنه — فقط از این
    عبور کنه.

    توجه: hospitals_service و fuel_service اینجا wire نشدن چون در این
    dependencies/services.py فعلی تعریف نشده بودن (به‌نظر می‌رسه
    api/hospitals.py و api/fuel.py هنوز به الگوی service/DI منتقل نشدن).
    وقتی اون سرویس‌ها ساخته شدن، همینجا به MedicalExpert/TransportExpert
    اضافه‌شون کنید.
    """
    rag = _get_rag_pipeline()
    weather = WeatherProvider()

    tourism = TourismExpert(rag, weather=weather)
    traffic = TrafficExpert(rag, hotspot_repository=hotspot_service, camera_repository=camera_service)
    medical = MedicalExpert(rag, hospitals_service=None)  # TODO: wire once a HospitalsService/DI exists
    transport = TransportExpert(rag, fuel_service=None)   # TODO: wire once a FuelService/DI exists

    return CopilotGateway(
        rag=rag,
        voice=None,  # wire VoicePipeline here once SpeechInterface() is constructed for this deployment
        analytics_service=analytics_service,
        tourism=tourism,
        traffic=traffic,
        medical=medical,
        transport=transport,
    )


# ============================================================
# Chat Service
# ============================================================
# Defined last because it depends on get_copilot_gateway above.

def get_chat_service(
    db: Session = Depends(get_db),
    gateway: CopilotGateway = Depends(get_copilot_gateway),
) -> ChatService:
    """
    دریافت سرویس چت‌بات

    Returns:
        ChatService: سرویس چت‌بات
    """
    return ChatService(db, gateway)
