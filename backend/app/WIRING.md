# اتصال قطعات به هم

این فایل نشون میده چطور همه‌ی providers/pipelines/experts رو در یک `CopilotGateway`
جمع کنید و از `services/chat_service.py` صداش کنید. **آپدیت شده** بر اساس فایل‌های
واقعی که فرستادید (`knowledge_base.py`, `graph_store.py`, `vector_store.py`,
`embedding_service.py`, `speech_interface.py`) — دیگه حدسی نیست.

## نکات کلیدی درباره‌ی موتورهای واقعی‌تون

- هر سه‌ی `KnowledgeBase` / `GraphStore` / `VectorStore` کاملاً **synchronous**
  هستن (JSON روی دیسک + عملیات درون‌حافظه‌ای) و هرکدوم یک factory تک‌نمونه
  دارن: `get_knowledge_base()`, `get_graph_store()`, `get_vector_store()`.
  providerها این factoryها رو صدا می‌زنن، نه ساخت instance جدید.
- `GraphStore` متد `traverse()` نداره؛ متد واقعیش `search(query, limit, max_depth)`
  هست (روی nodes و edge-relations هر دو جستجو می‌کنه) به‌علاوه‌ی `get_neighbors(node_id)`.
- `VectorStore.search(query, top_k, threshold)` خودش متن رو embed می‌کنه —
  لازم نیست embedding رو جدا بسازید و پاس بدید.
- `SpeechInterface` هم sync هست و روی **فایل** کار می‌کنه، نه bytes خام:
  `speech_to_text(audio_file=..., language="fa-IR") -> (text, confidence)` و
  `text_to_speech_bytes(text, language="fa") -> bytes`. توی خود ماژول فقط
  `speech_interface = None` تعریف شده — یعنی خودتون باید `SpeechInterface()`
  بسازید و پاس بدید؛ من این کار رو در `VoicePipeline` انجام دادم (نوشتن bytes
  آپلودی روی یک فایل موقت قبل از فراخوانی `speech_to_text`).
- `speech_recognition` / `gtts` / `pyttsx3` کتابخانه‌ی third-party هستن (نه
  stdlib) — طبق کد واقعی خودتون همینه، پس محدودیت stdlib-only ظاهراً فقط
  روی بعضی ماژول‌ها (مثل engine_adapter.py) اعمال شده، نه همه‌جا. اگه می‌خواید
  این سرویس هم offline-first/stdlib-only بشه باید جدا هماهنگ بشه.

## 1. ساخت Gateway (یک‌بار، در startup)

جای مناسب: `dependencies/services.py` یا یک `container.py` جدید که در `main.py`
هنگام startup ساخته میشه و بین request ها به اشتراک گذاشته میشه (تک نمونه).

```python
# dependencies/services.py  (افزودن به فایل موجود)

from core.engine.hybrid.knowledge_base import get_knowledge_base
from core.engine.hybrid.graph_store import get_graph_store
from core.engine.hybrid.vector_store import get_vector_store
from core.speech_interface import SpeechInterface

from providers.bandari_provider import BandariProvider
from providers.knowledge_provider import KnowledgeProvider
from providers.graph_provider import GraphProvider
from providers.vector_provider import VectorProvider
from providers.weather_provider import WeatherProvider
from pipelines.search_pipeline import SearchPipeline
from pipelines.rag_pipeline import RAGPipeline
from pipelines.voice_pipeline import VoicePipeline
from experts.tourism_expert import TourismExpert
from experts.traffic_expert import TrafficExpert
from experts.medical_expert import MedicalExpert
from experts.transport_expert import TransportExpert
from gateway.copilot_gateway import CopilotGateway


def build_copilot_gateway(
    llm_adapter,          # LLM adapter موجود در Bandari Engine
    analytics_service=None,
    hotspot_repository=None,
    camera_repository=None,
    hospitals_service=None,
    fuel_service=None,
    enable_voice: bool = True,
) -> CopilotGateway:
    bandari = BandariProvider()  # پیش‌فرض: http://127.0.0.1:5200

    # هر سه‌ی زیر از factory تک‌نمونه‌ی خودشون استفاده می‌کنن، پس همه‌ی
    # request ها یک instance مشترک از knowledge/graph/vector رو می‌بینن.
    knowledge = KnowledgeProvider(engine=get_knowledge_base())
    graph = GraphProvider(engine=get_graph_store())
    vector = VectorProvider(store=get_vector_store())
    weather = WeatherProvider()

    search = SearchPipeline(knowledge=knowledge, graph=graph, vector=vector)
    rag = RAGPipeline(bandari=bandari, search=search, llm=llm_adapter)

    # SpeechInterface خودش رو construct می‌کنه (ماژول فقط placeholder داره).
    speech_interface = SpeechInterface() if enable_voice else None
    voice = VoicePipeline(speech_interface, rag) if speech_interface else None

    tourism = TourismExpert(rag, weather=weather)
    traffic = TrafficExpert(rag, hotspot_repository=hotspot_repository, camera_repository=camera_repository)
    medical = MedicalExpert(rag, hospitals_service=hospitals_service)
    transport = TransportExpert(rag, fuel_service=fuel_service)

    return CopilotGateway(
        rag=rag,
        voice=voice,
        analytics_service=analytics_service,
        tourism=tourism,
        traffic=traffic,
        medical=medical,
        transport=transport,
    )
```

## 2. تزریق Gateway در FastAPI (dependencies/services.py)

```python
_gateway_singleton: CopilotGateway | None = None

def get_copilot_gateway() -> CopilotGateway:
    global _gateway_singleton
    if _gateway_singleton is None:
        _gateway_singleton = build_copilot_gateway(llm_adapter=your_llm_adapter)
    return _gateway_singleton
```

## 3. صدا زدن از services/chat_service.py

قبلاً `chat_service.py` مستقیماً باید Bandari رو صدا میزد. حالا این مسئولیت
داخل `RAGPipeline` هست، پس `chat_service.py` فقط Gateway رو صدا میزنه:

```python
# services/chat_service.py

from dependencies.services import get_copilot_gateway

async def handle_chat_message(text: str, session_id: str | None = None) -> dict:
    gateway = get_copilot_gateway()
    response = await gateway.handle_message(text, session_id=session_id)
    return {
        "intent": response.intent,
        "expert": response.expert,
        "answer": response.answer,
        "sources": [s.__dict__ for s in response.sources],
        "extra": response.extra,
    }
```

## 4. صدا زدن از endpoints/voice.py

```python
from dependencies.services import get_copilot_gateway

async def handle_voice_upload(audio_bytes: bytes, session_id: str | None = None):
    gateway = get_copilot_gateway()
    result = await gateway.handle_voice(audio_bytes, session_id=session_id)
    return {
        "transcript": result.transcript,
        "confidence": result.confidence,
        "answer": result.answer_text,
        # result.audio -> bytes قابل استریم به کلاینت، اگه want_audio_reply=True بوده
    }
```

## نکات مهم

- **هیچ endpoint دیگه‌ای نباید مستقیماً provider/pipeline/expert رو صدا بزنه** —
  فقط از `CopilotGateway` عبور کنه. این همون قانونیه که خودتون در مرحله ۴ خواستید.
- همه‌ی متدهای موتورهای واقعی (`KnowledgeBase.search`, `GraphStore.search`,
  `VectorStore.search`) sync هستن؛ providerها با `loop.run_in_executor` این
  کارها رو off-load می‌کنن تا event loop بلاک نشه.
- همه‌ی HTTP call ها به Bandari Engine از طریق `urllib` (stdlib) هستن.
- `BaseProvider` یک circuit breaker سبک داره؛ اگه یک موتور یا Bandari Engine
  خطا بده، Gateway کرش نمی‌کنه، فقط اون بخش رو skip می‌کنه (نتایج ناقص‌تر،
  نه شکست کامل).
- اگه فایل واقعی `chat_service.py` یا `endpoints/chat.py` رو هم بفرستید،
  می‌تونم مستقیم پچ (diff) بدم به‌جای اینکه فقط نمونه بنویسم.
