import time
from typing import Dict, Any, List
from src.core.intent_router import IntentRouter, Intent
from src.core.expert_selector import ExpertSelector, ExpertPlan
from src.core.query_planner import QueryPlanner, PlanStep
from src.retrieval.rag_engine import RagEngine
from src.output.synthesizer import Synthesizer
from src.tools.google_gemini import GoogleGeminiTool
from src.tools.local_llm import LocalLlmTool
from src.tools.levels import LevelsTool

class HdpOrchestrator:
    def __init__(self):
        self.router = IntentRouter()
        self.selector = ExpertSelector()
        self.planner = QueryPlanner()
        self.rag = RagEngine()
        self.synth = Synthesizer()
        self.gemini = GoogleGeminiTool()
        self.local_llm = LocalLlmTool()
        self.levels = LevelsTool()

    async def process(self, query: str, use_ai: str = "auto") -> Dict[str, Any]:
        t0 = time.time()

        intent = self.router.route(query)
        plan = self.selector.select(intent)
        steps = self.planner.create_plan(intent, intent.entities)
        retrieved = self.rag.retrieve(query, intent.name, steps)
        ai_answer = await self._generate(query, retrieved, use_ai)
        answer = self.synth.synthesize(query, intent, retrieved, ai_answer)

        return {
            "query": query,
            "intent": {"name": intent.name, "confidence": intent.confidence},
            "experts": {"primary": plan.primary, "supporting": plan.supporting},
            "retrieved_count": len(retrieved),
            "answer": answer,
            "processing_time_ms": int((time.time() - t0) * 1000),
        }

    async def _generate(self, query: str, context: List[Dict], mode: str) -> str:
        if mode == "gemini" and self.gemini.available:
            return await self.gemini.generate(query, context)
        elif mode == "local" and self.local_llm.available:
            return await self.local_llm.generate(query, context)
        elif mode == "levels" and self.levels.available:
            return await self.levels.generate(query, context)
        elif self.gemini.available:
            return await self.gemini.generate(query, context)
        elif self.local_llm.available:
            return await self.local_llm.generate(query, context)
        else:
            return self.synth.fallback(query, context)
