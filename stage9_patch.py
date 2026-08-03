#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# HDP Stage 8 - Deploy All Patches
# ============================================================

echo ""
echo "============================================================"
echo "🚀 HDP Stage 8 - Deploying Patches"
echo "============================================================"
echo ""

# ============================================================
# Paths
# ============================================================

ROOT=$HOME/hermezgan-intelligent
BACKEND=$ROOT/backend
APP=$BACKEND/app

echo "📁 Root: $ROOT"
echo ""

# ============================================================
# Create directories
# ============================================================

mkdir -p $APP/core/engine
mkdir -p $APP/api/v1/endpoints
mkdir -p $APP/gateway
mkdir -p $APP/search
mkdir -p $APP/services

# ============================================================
# 1. orchestrator_v2.py
# ============================================================

cat > $APP/core/orchestrator_v2.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Orchestrator V2
Unified request/response processing
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

logger = logging.getLogger("hdp.orchestrator")


@dataclass
class UnifiedRequest:
    request_id: str
    session_id: str
    user_id: str
    input_type: str
    text: str
    context: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class UnifiedResponse:
    response: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    audio: bytes | None = None


class HDPOrchestrator:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_ready", False):
            return
        self._ready = True
        self.copilot = None
        self.search_pipeline = None
        self.hybrid_engine = None
        self.tts = None
        self.bandari = None
        self.sessions = {}

    def initialize(
        self,
        *,
        copilot,
        search_pipeline,
        hybrid_engine,
        bandari=None,
        tts=None,
    ):
        self.copilot = copilot
        self.search_pipeline = search_pipeline
        self.hybrid_engine = hybrid_engine
        self.bandari = bandari
        self.tts = tts
        logger.info("✅ HDP Orchestrator Ready")

    async def process(self, req: UnifiedRequest):
        # Bandari analysis
        if self.bandari:
            bandari_result = await self.bandari.analyze(req.text, req.context)
            normalized = bandari_result.get("normalized_text", req.text)
            dialect = bandari_result.get("dialect", "standard")
            intent = bandari_result.get("intent", "general")
        else:
            normalized = req.text
            dialect = "standard"
            intent = "general"

        # Search
        retrieval = []
        if self.search_pipeline:
            retrieval = await self.search_pipeline.search(
                query=normalized,
                intent=intent,
                dialect=dialect,
                top_k=5
            )

        # Copilot
        result = await self.copilot.handle_message(
            message={
                "content": normalized,
                "metadata": {
                    "dialect": dialect,
                    "intent": intent,
                    "retrieval": retrieval
                }
            },
            session_id=req.session_id,
            user_id=req.user_id
        )

        # TTS
        audio = None
        if self.tts and req.input_type == "voice":
            audio = await self.tts.synthesize(result["response"], language="fa")

        return UnifiedResponse(
            response=result["response"],
            sources=result.get("sources", []),
            metadata=result.get("metadata", {}),
            audio=audio
        )

    async def process_text(self, session_id, user_id, text, context=None):
        req = UnifiedRequest(
            request_id=session_id,
            session_id=session_id,
            user_id=user_id,
            input_type="text",
            text=text,
            context=context or {},
        )
        return await self.process(req)

    async def process_voice(self, session_id, user_id, transcript, context=None):
        req = UnifiedRequest(
            request_id=session_id,
            session_id=session_id,
            user_id=user_id,
            input_type="voice",
            text=transcript,
            context=context or {},
        )
        return await self.process(req)


_orchestrator = HDPOrchestrator()


def get_orchestrator():
    return _orchestrator
EOF

echo "✅ orchestrator_v2.py"

# ============================================================
# 2. copilot_gateway.py
# ============================================================

cat > $APP/gateway/copilot_gateway.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

logger = logging.getLogger("hdp.copilot")


class CopilotGateway:

    def __init__(
        self,
        search_pipeline=None,
        hybrid_engine=None,
        llm_client=None,
        tts_client=None,
    ):
        self.search_pipeline = search_pipeline
        self.hybrid_engine = hybrid_engine
        self.llm_client = llm_client
        self.tts_client = tts_client

    async def handle_message(
        self,
        message: Dict[str, Any],
        session_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        query = message.get("content", "")
        metadata = message.get("metadata", {})
        dialect = metadata.get("dialect", "standard")
        intent = metadata.get("intent", "general")

        documents = []
        if self.search_pipeline:
            documents = await self.search_pipeline.search(
                query=query,
                dialect=dialect,
                intent=intent,
                top_k=5,
            )
        elif self.hybrid_engine:
            documents = await self.hybrid_engine.search(
                query=query,
                limit=5,
            )

        context = []
        for doc in documents:
            text = doc.get("text", "")
            source = doc.get("source", "knowledge")
            context.append(f"[{source}]\n{text}")

        rag_context = "\n\n".join(context)
        prompt = self.build_prompt(
            query=query,
            context=rag_context,
            dialect=dialect,
            intent=intent,
        )

        if self.llm_client:
            answer = await self.llm_client.generate(
                prompt=prompt,
                session_id=session_id,
            )
        else:
            answer = "LLM Client Not Configured"

        return {
            "response": answer,
            "sources": documents,
            "metadata": {
                "dialect": dialect,
                "intent": intent,
                "retrieval_count": len(documents),
                "session_id": session_id,
                "user_id": user_id,
            },
        }

    def build_prompt(self, query, context, dialect, intent):
        return f"""
شما موتور مرکزی HDP هستید.

گویش: {dialect}
هدف: {intent}

دانش بازیابی شده:
{context}

سؤال: {query}

فقط بر اساس اطلاعات بازیابی شده پاسخ بده.
اگر اطلاعات کافی نبود اعلام کن.
"""
EOF

echo "✅ copilot_gateway.py"

# ============================================================
# 3. search_pipeline.py
# ============================================================

cat > $APP/search/search_pipeline.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import logging

logger = logging.getLogger("hdp.search")


class SearchPipeline:

    def __init__(self, hybrid_engine):
        self.hybrid_engine = hybrid_engine

    async def search(
        self,
        query: str,
        intent: str = "general",
        dialect: str = "standard",
        top_k: int = 5,
    ):
        logger.info(f"SearchPipeline query={query}")
        result = await self.hybrid_engine.search(
            query=query,
            intent=intent,
            dialect=dialect,
            limit=top_k,
        )
        return result
EOF

echo "✅ search_pipeline.py"

# ============================================================
# 4. hybrid_engine.py
# ============================================================

cat > $APP/core/engine/hybrid_engine.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import aiosqlite
from typing import List, Dict


class HybridEngine:

    def __init__(self, db_path):
        self.db_path = db_path

    async def search(
        self,
        query,
        intent="general",
        dialect="standard",
        limit=5,
    ) -> List[Dict]:
        sql = """
        SELECT id, title, content, category
        FROM knowledge
        WHERE knowledge MATCH ?
        LIMIT ?
        """
        docs = []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, (query, limit)) as cursor:
                rows = await cursor.fetchall()

        for row in rows:
            docs.append({
                "id": row["id"],
                "title": row["title"],
                "text": row["content"],
                "source": row["category"],
                "score": 1.0,
            })
        return docs
EOF

echo "✅ hybrid_engine.py"

# ============================================================
# 5. orchestrator_service.py
# ============================================================

cat > $APP/services/orchestrator_service.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.core.orchestrator_v2 import get_orchestrator
from app.gateway.copilot_gateway import CopilotGateway
from app.search.search_pipeline import SearchPipeline
from app.core.engine.hybrid_engine import HybridEngine


class OrchestratorService:

    def __init__(self):
        hybrid = HybridEngine(db_path="data/hdp_v2.db")
        pipeline = SearchPipeline(hybrid)
        gateway = CopilotGateway(
            search_pipeline=pipeline,
            hybrid_engine=hybrid,
        )
        orchestrator = get_orchestrator()
        orchestrator.initialize(
            copilot=gateway,
            search_pipeline=pipeline,
            hybrid_engine=hybrid,
            bandari=None,
            tts=None,
        )
        self.orchestrator = orchestrator

    async def process(
        self,
        session_id,
        user_id,
        text,
        context=None,
    ):
        return await self.orchestrator.process_text(
            session_id=session_id,
            user_id=user_id,
            text=text,
            context=context or {},
        )
EOF

echo "✅ orchestrator_service.py"

# ============================================================
# 6. speech_to_text.py
# ============================================================

cat > $APP/core/speech_to_text.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import json
import os
from vosk import Model, KaldiRecognizer


class SpeechToText:

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.expanduser(
                "~/hermezgan-intelligent/bandari-engine-2026/bandari-engine/speech/vosk/model"
            )
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)

    def process_chunk(self, chunk: bytes):
        if self.recognizer.AcceptWaveform(chunk):
            return json.loads(self.recognizer.Result()).get("text", "")
        return ""

    def finalize(self):
        return json.loads(self.recognizer.FinalResult()).get("text", "")
EOF

echo "✅ speech_to_text.py"

# ============================================================
# 7. voice.py (endpoint)
# ============================================================

cat > $APP/api/v1/endpoints/voice.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.orchestrator_v2 import get_orchestrator
from app.core.speech_to_text import SpeechToText

router = APIRouter()


@router.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    await websocket.accept()
    orchestrator = get_orchestrator()
    stt = SpeechToText()
    session = str(uuid.uuid4())
    user = "anonymous"
    await websocket.send_json({"type": "connected", "session_id": session})

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                text = stt.process_chunk(message["bytes"])
                if text:
                    await websocket.send_json({"type": "partial", "text": text})
            elif "text" in message:
                payload = json.loads(message["text"])
                if payload["type"] == "finalize":
                    transcript = stt.finalize()
                    result = await orchestrator.process_voice(
                        session_id=session,
                        user_id=user,
                        transcript=transcript
                    )
                    await websocket.send_json({
                        "type": "response",
                        "text": result.response,
                        "sources": result.sources,
                        "metadata": result.metadata
                    })
                    if result.audio:
                        await websocket.send_bytes(result.audio)
    except WebSocketDisconnect:
        pass
EOF

echo "✅ voice.py"

# ============================================================
# 8. speech_interface.py
# ============================================================

cat > $APP/core/speech_interface.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
from pathlib import Path


class BandariSpeechInterface:

    def __init__(self):
        self.root = (
            Path.home()
            / "hermezgan-intelligent"
            / "bandari-engine-2026"
            / "bandari-engine"
        )

    async def analyze(self, text):
        process = await asyncio.create_subprocess_exec(
            "node",
            str(self.root / "index.js"),
            "analyze",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.root),
        )
        stdout, _ = await process.communicate(
            json.dumps({"text": text}).encode()
        )
        return json.loads(stdout.decode())
EOF

echo "✅ speech_interface.py"

# ============================================================
# 9. main.py
# ============================================================

cat > $APP/main.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.orchestrator_service import OrchestratorService

orchestrator_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator_service
    orchestrator_service = OrchestratorService()
    app.state.orchestrator = orchestrator_service
    print("=" * 60)
    print("🚀 HDP AI CORE READY")
    print("=" * 60)
    yield
    print("🛑 Stopping HDP...")


app = FastAPI(
    title="Hormozgan Intelligent",
    version="8.0",
    lifespan=lifespan
)

# Chat
from app.api.chat import router as chat_router
app.include_router(chat_router, prefix="/api")

# Voice
from app.api.v1.endpoints.voice import router as voice_router
app.include_router(voice_router, prefix="/api/v1")
EOF

echo "✅ main.py"

# ============================================================
# 10. container.py
# ============================================================

cat > $APP/core/container.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app.core.orchestrator_v2 import get_orchestrator
from app.gateway.copilot_gateway import CopilotGateway
from app.search.search_pipeline import SearchPipeline
from app.core.engine.hybrid_engine import HybridEngine
from app.core.speech_interface import BandariSpeechInterface


class Container:

    def __init__(self):
        hybrid = HybridEngine(db_path="data/hdp_v2.db")
        pipeline = SearchPipeline(hybrid)
        bandari = BandariSpeechInterface()
        gateway = CopilotGateway(
            search_pipeline=pipeline,
            hybrid_engine=hybrid,
        )
        orchestrator = get_orchestrator()
        orchestrator.initialize(
            copilot=gateway,
            search_pipeline=pipeline,
            hybrid_engine=hybrid,
            bandari=bandari,
            tts=None,
        )
        self.orchestrator = orchestrator


container = Container()
EOF

echo "✅ container.py"

# ============================================================
# 11. health_check.py
# ============================================================

cat > $ROOT/health_check.py << 'EOF'
#!/usr/bin/env python3

from pathlib import Path

ROOT = Path.home() / "hermezgan-intelligent"

CHECKS = [
    ROOT / "backend",
    ROOT / "backend/data/hdp_v2.db",
    ROOT / "bandari-engine-2026",
    ROOT / "backend/app/main.py",
    ROOT / "backend/app/core/orchestrator_v2.py",
]

ok = True
for item in CHECKS:
    if item.exists():
        print("[ OK ]", item)
    else:
        print("[FAIL]", item)
        ok = False

exit(0 if ok else 1)
EOF

echo "✅ health_check.py"

# ============================================================
# 12. start_hdp.sh
# ============================================================

cat > $ROOT/start_hdp.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT=$HOME/hermezgan-intelligent
cd $ROOT/backend
source venv/bin/activate
python $
