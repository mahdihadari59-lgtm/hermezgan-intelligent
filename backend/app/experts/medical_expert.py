"""
experts/medical_expert.py

Scope is strictly informational: hospital/clinic locations, hours, services,
emergency numbers — sourced from the existing hospitals API/knowledge
content. This expert must never attempt diagnosis or treatment advice; the
system prompt fed to the LLM in RAGPipeline should make that boundary
explicit for this category.
"""

from __future__ import annotations

from typing import Any

from app.experts import BaseExpert
from app.pipelines.rag_pipeline import RAGResult

_SAFETY_NOTE = (
    "این پاسخ صرفاً اطلاعات مربوط به مراکز درمانی است و جایگزین مشاوره پزشکی نیست. "
    "در شرایط اورژانسی با ۱۱۵ تماس بگیرید."
)


class MedicalExpert(BaseExpert):
    domain = "medical"
    category = "medical"

    def __init__(self, rag, hospitals_service: Any = None):
        super().__init__(rag)
        self.hospitals_service = hospitals_service

    async def enrich(self, user_text: str, result: RAGResult) -> dict:
        extra: dict = {"safety_note": _SAFETY_NOTE}

        if self.hospitals_service is not None and hasattr(self.hospitals_service, "search_nearby"):
            try:
                extra["hospitals"] = self.hospitals_service.search_nearby(user_text)
            except Exception:  # noqa: BLE001
                extra["hospitals"] = []

        return extra
