"""
pipelines/rag_pipeline.py

Implements the routing you specified:

    User -> Intent -> Bandari Engine -> Knowledge Base -> Hybrid Ranker
         -> FastAPI -> Frontend

Step by step:
1. Raw user text is sent to BandariProvider to detect dialect and get a
   Standard Persian normalization (Bandari/Minabi/Qeshmi/Bastaki -> fa-IR).
2. The normalized text drives SearchPipeline (knowledge + graph + vector).
3. Retrieved context + the ORIGINAL (dialect) text are handed to the LLM
   adapter so the reply can optionally be re-rendered back in the user's
   dialect for a more natural chat experience.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

from app.providers import ProviderError
from app.providers.bandari_provider import BandariProvider
from app.pipelines.search_pipeline import RankedResult, SearchPipeline

logger = logging.getLogger("hdp.pipelines.rag")


@dataclass
class RAGResult:
    answer: str
    dialect: Optional[str]
    normalized_query: str
    sources: list[RankedResult]


class RAGPipeline:
    def __init__(self, bandari: BandariProvider, search: SearchPipeline, llm: Any):
        """
        `llm` is your existing pluggable LLM adapter (already built as part
        of the Bandari Engine's 8-layer architecture, or a separate
        generation client) — anything exposing an async
        `generate(prompt: str) -> str` method.
        """
        self.bandari = bandari
        self.search = search
        self.llm = llm

    async def answer(self, user_text: str, category: str | None = None) -> RAGResult:
        dialect_info = await self._detect_and_normalize(user_text)
        normalized = dialect_info.get("normalized", user_text)
        dialect = dialect_info.get("dialect")

        sources = await self.search.run(normalized, category=category)

        prompt = self._build_prompt(user_text, normalized, dialect, sources)
        answer = await self._generate(prompt, fallback_sources=sources)

        return RAGResult(answer=answer, dialect=dialect, normalized_query=normalized, sources=sources)

    async def _detect_and_normalize(self, text: str) -> dict:
        try:
            return await self.bandari.translate(text, direction="auto")
        except ProviderError as exc:
            logger.warning("rag_pipeline: bandari normalization unavailable, using raw text: %s", exc)
            return {"normalized": text, "dialect": None}

    def _build_prompt(
        self, original: str, normalized: str, dialect: str | None, sources: list[RankedResult]
    ) -> str:
        context_block = "\n".join(f"- {r.title}: {r.content}" for r in sources[:5]) or "(no matching context found)"
        dialect_note = f"User's dialect: {dialect}. Reply naturally in this dialect if appropriate.\n" if dialect else ""
        return (
            f"{dialect_note}"
            f"User question (normalized): {normalized}\n\n"
            f"Relevant context:\n{context_block}\n\n"
            f"Answer the user's question using only the context above. "
            f"If the context is insufficient, say so honestly."
        )

    async def _generate(self, prompt: str, fallback_sources: list[RankedResult]) -> str:
        try:
            return await self.llm.generate(prompt)
        except Exception as exc:  # noqa: BLE001 - generation must never crash the request
            logger.error("rag_pipeline: LLM generation failed, falling back to top source: %s", exc)
            if fallback_sources:
                return fallback_sources[0].content
            return "متاسفانه در حال حاضر امکان پاسخ‌گویی وجود ندارد."
