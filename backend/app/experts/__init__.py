"""
experts/__init__.py

Domain experts are thin, opinionated wrappers around RAGPipeline: each one
pins a `category` filter and adds domain-specific enrichment/formatting.
CopilotGateway picks which expert(s) to consult based on detected intent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.pipelines.rag_pipeline import RAGPipeline, RAGResult


@dataclass
class ExpertResponse:
    expert: str
    answer: str
    sources: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)


class BaseExpert:
    domain: str = "generic"
    category: str | None = None

    def __init__(self, rag: RAGPipeline):
        self.rag = rag

    async def answer(self, user_text: str) -> ExpertResponse:
        result: RAGResult = await self.rag.answer(user_text, category=self.category)
        extra = await self.enrich(user_text, result)
        return ExpertResponse(expert=self.domain, answer=result.answer, sources=result.sources, extra=extra)

    async def enrich(self, user_text: str, result: RAGResult) -> dict:
        """Override in subclasses to attach domain-specific extras (weather, live traffic, etc.)."""
        return {}
