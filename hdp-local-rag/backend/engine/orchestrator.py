#!/usr/bin/env python3
"""
orchestrator.py
------------------
همان حلقه‌ای که در ممیزی به‌عنوان "؟" علامت‌گذاری شده بود:

    API -> AI Router -> Search Manager -> [FTS/Graph/Hybrid/Synonym] -> ؟ -> Answer

این فایل آن "؟" است. مسئولیت‌هایش:
  1. صدا زدن Intent Engine
  2. صدا زدن Coordinator برای اجرای موازی موتورهای جستجو
  3. صدا زدن Ranking Engine (یا fallback داخلی اگر ثبت نشده)
  4. صدا زدن Expert Dispatcher بر اساس domain تشخیص داده‌شده
  5. صدا زدن Answer Engine با Context کامل (نه فقط query خام —
     دقیقاً مشکلی که در ممیزی Answer Engine ذکر شده بود)
  6. ثبت زمان و خطای هر مرحله برای متریک/دیباگ

هر مرحله ایزوله است: اگر یک مرحله (مثلاً Expert) خطا بدهد، پایپ‌لاین با
یک نتیجه degraded ادامه می‌دهد به‌جای کرش کامل — چون در سیستم زنده،
جواب ضعیف بهتر از هیچ جواب است.

فقط stdlib.
"""

import logging
import time
from typing import Optional

from contracts import (
    ExecutionContext, EngineKind, RankedItem, AnswerResult,
)
from engine_registry import EngineRegistry
from coordinator import Coordinator

logger = logging.getLogger("hdp.orchestrator")


class Orchestrator:
    def __init__(self, registry: EngineRegistry, per_engine_timeout_s: float = 3.0):
        self.registry = registry
        self.coordinator = Coordinator(
            registry.get_search_engines(), per_engine_timeout_s=per_engine_timeout_s
        )

    async def _timed_stage(self, ctx: ExecutionContext, stage_name: str, coro):
        start = time.monotonic()
        try:
            result = await coro
            ctx.stage_timings_ms[stage_name] = (time.monotonic() - start) * 1000
            return result
        except Exception as e:  # noqa: BLE001 — ایزوله‌سازی خطای هر مرحله
            ctx.stage_timings_ms[stage_name] = (time.monotonic() - start) * 1000
            ctx.stage_errors[stage_name] = str(e)
            logger.exception("مرحله '%s' خطا داد", stage_name)
            return None

    # ------------------------------------------------------------------
    def _default_rank(self, ctx: ExecutionContext) -> list[RankedItem]:
        """
        Ranking پیش‌فرض: fusion ساده وزنی روی نتایج همه موتورهای جستجو.
        اگر یک RankingEngine واقعی (scorer/rerank موجودت) ثبت شده باشد،
        این تابع اصلاً صدا زده نمی‌شود — این فقط fallback است تا پایپ‌لاین
        همیشه یک خروجی مرتب‌شده داشته باشد.
        """
        merged: dict[str, RankedItem] = {}
        for sr in ctx.search_results:
            if sr.error:
                continue
            for hit in sr.hits:
                if hit.doc_id not in merged:
                    merged[hit.doc_id] = RankedItem(
                        doc_id=hit.doc_id, final_score=0.0,
                        title=hit.title, snippet=hit.snippet, metadata=hit.metadata,
                    )
                item = merged[hit.doc_id]
                item.final_score += hit.score
                item.contributing_engines.append(hit.source_engine)

        # امتیاز اسناد چندموتوره را کمی تقویت می‌کنیم (رأی‌گیری بین موتورها)
        for item in merged.values():
            n = len(set(item.contributing_engines))
            if n > 1:
                item.final_score *= (1.0 + 0.1 * (n - 1))

        return sorted(merged.values(), key=lambda x: x.final_score, reverse=True)

    # ------------------------------------------------------------------
    async def process(self, raw_query: str, *, user_id: Optional[str] = None,
                       locale: str = "fa-IR") -> AnswerResult:
        ctx = ExecutionContext(raw_query=raw_query, user_id=user_id, locale=locale)
        logger.info("[%s] شروع پردازش: %r", ctx.trace_id, raw_query)

        # ۱. Intent
        if self.registry.has(EngineKind.INTENT):
            intent_engine = self.registry.get(EngineKind.INTENT)
            ctx.intent = await self._timed_stage(ctx, "intent", intent_engine.detect(ctx))

        # ۲. Search (موازی، از طریق Coordinator)
        await self._timed_stage(ctx, "search", self.coordinator.run(ctx))

        # ۳. Ranking
        if self.registry.has(EngineKind.RANKING):
            ranking_engine = self.registry.get(EngineKind.RANKING)
            ranked = await self._timed_stage(ctx, "ranking", ranking_engine.rank(ctx))
            ctx.ranked_results = ranked or self._default_rank(ctx)
        else:
            start = time.monotonic()
            ctx.ranked_results = self._default_rank(ctx)
            ctx.stage_timings_ms["ranking_fallback"] = (time.monotonic() - start) * 1000

        # ۴. Expert Dispatch
        if self.registry.has(EngineKind.EXPERT):
            expert_engine = self.registry.get(EngineKind.EXPERT)
            ctx.expert_result = await self._timed_stage(ctx, "expert", expert_engine.dispatch(ctx))

        # ۵. Answer — با Context کامل (intent + ranked_results + expert_result)
        if self.registry.has(EngineKind.ANSWER):
            answer_engine = self.registry.get(EngineKind.ANSWER)
            answer = await self._timed_stage(ctx, "answer", answer_engine.generate(ctx))
        else:
            answer = None

        if answer is None:
            # Degraded fallback: حتی بدون Answer Engine واقعی، چیزی برمی‌گردانیم
            top = ctx.ranked_results[:3]
            text = "؛ ".join(t.title or t.doc_id for t in top) if top else "نتیجه‌ای پیدا نشد."
            answer = AnswerResult(text=text, sources=[t.doc_id for t in top],
                                   confidence=0.3, trace_id=ctx.trace_id,
                                   debug={"degraded": True})

        answer.trace_id = ctx.trace_id
        answer.debug.setdefault("stage_timings_ms", ctx.stage_timings_ms)
        answer.debug.setdefault("stage_errors", ctx.stage_errors)
        answer.debug.setdefault("total_ms", ctx.elapsed_ms())

        logger.info("[%s] پایان پردازش در %.1fms", ctx.trace_id, ctx.elapsed_ms())
        return answer
