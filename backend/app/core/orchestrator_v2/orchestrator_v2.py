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
