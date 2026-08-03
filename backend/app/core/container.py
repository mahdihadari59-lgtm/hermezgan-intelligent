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
