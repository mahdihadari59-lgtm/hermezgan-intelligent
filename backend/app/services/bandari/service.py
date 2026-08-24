from __future__ import annotations
import re
from typing import Any, Optional
from sqlalchemy import select, or_, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from .models import BandariWord, LocalKnowledge, GrammarRule, Idiom, Dialogue
from .schemas import DetectionResult, TranslationResult
from .exceptions import BandariEngineError

DIALECTS = ("ban", "min", "qes", "jas", "lan", "bas", "kha", "rud", "sir")
DIALECT_LABELS = {
    "ban": "bandari",
    "min": "minabi",
    "qes": "qeshmi",
    "jas": "jask",
    "lan": "langavi",
    "bas": "bastaki",
    "kha": "khaviji",
    "rud": "rudani",
    "sir": "siriki",
}

class BandariServiceV6:
    """Internal Python Bandari service. No Node.js dependency."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_word(self, word: str, dialect: str = "ban", limit: int = 20) -> list[dict[str, Any]]:
        if dialect not in DIALECTS:
            dialect = "ban"
        q = f"%{word}%"
        stmt = select(BandariWord).where(
            BandariWord.dialect_code == dialect,
            or_(BandariWord.word_standard.ilike(q), BandariWord.word_bandari.ilike(q))
        ).limit(limit)
        rows = (await self.db.execute(stmt)).scalars().all()
        return [self._word(r) for r in rows]

    async def translate(self, text: str, source: str = "persian", target: str = "ban") -> TranslationResult:
        text = text.strip()
        if not text:
            raise BandariEngineError("text is required")
        target = target if target in DIALECTS else "ban"
        if source == "persian":
            stmt = select(BandariWord).where(
                BandariWord.word_standard.ilike(text), BandariWord.dialect_code == target
            )
        else:
            stmt = select(BandariWord).where(
                BandariWord.word_bandari.ilike(text), BandariWord.dialect_code == source
            )
        row = (await self.db.execute(stmt)).scalar_one_or_none()
        if row:
            translated = row.word_bandari if source == "persian" else row.word_standard
            return TranslationResult(translated or text, normalized_text=row.word_standard,
                raw={"source": "database", "data_quality": row.data_quality, "confidence": row.confidence_score})
        # Phrase fallback: normalize known words independently.
        pieces = re.findall(r"[^\s]+", text)
        out = []
        found = 0
        for piece in pieces:
            s = await self.db_translate_piece(piece, source, target)
            out.append(s["translated"] if s else piece)
            found += bool(s)
        if found:
            return TranslationResult(" ".join(out), normalized_text=text,
                raw={"source": "database", "partial": True, "matched_words": found})
        return TranslationResult(text, normalized_text=text,
            raw={"source": "database", "untranslated": True})

    async def db_translate_piece(self, word: str, source: str, target: str):
        if source == "persian":
            stmt = select(BandariWord).where(BandariWord.word_standard.ilike(word), BandariWord.dialect_code == target)
        else:
            stmt = select(BandariWord).where(BandariWord.word_bandari.ilike(word), BandariWord.dialect_code == source)
        row = (await self.db.execute(stmt)).scalar_one_or_none()
        if not row:
            return None
        return {"translated": row.word_bandari if source == "persian" else row.word_standard,
                "confidence": row.confidence_score}

    async def detect(self, text: str) -> DetectionResult:
        """Database-first dialect detection using exact vocabulary matches."""
        tokens = [t for t in re.findall(r"[\u0600-\u06FF\w]+", text.lower()) if len(t) >= 2]
        if not tokens:
            return DetectionResult("fa", 0.0, "fa", {"reason": "no_tokens"})
        scores = {d: 0 for d in DIALECTS}
        for token in tokens:
            stmt = select(BandariWord.dialect_code).where(
                or_(BandariWord.word_bandari.ilike(token), BandariWord.word_standard.ilike(token))
            ).limit(20)
            codes = (await self.db.execute(stmt)).scalars().all()
            for code in codes:
                if code in scores:
                    scores[code] += 1
        best = max(scores, key=scores.get)
        hits = scores[best]
        confidence = min(1.0, hits / max(1, min(len(tokens), 5))) if hits else 0.0
        dialect = DIALECT_LABELS.get(best, best) if hits else "fa"
        language = "fa" if not hits else dialect
        return DetectionResult(dialect, confidence, language, {"scores": scores, "tokens": len(tokens)})

    async def categories(self):
        rows = (await self.db.execute(select(distinct(BandariWord.category)).where(BandariWord.category.isnot(None)))).scalars().all()
        return [{"key": c, "label": c} for c in rows if c]

    async def knowledge(self, category: Optional[str] = None, region: Optional[str] = None, limit: int = 50):
        stmt = select(LocalKnowledge)
        if category: stmt = stmt.where(LocalKnowledge.category == category)
        if region: stmt = stmt.where(LocalKnowledge.region.ilike(f"%{region}%"))
        rows = (await self.db.execute(stmt.limit(limit))).scalars().all()
        return [{"id": r.id, "title": r.title, "content": r.content, "category": r.category,
                 "subcategory": r.subcategory, "example": r.example, "region": r.region,
                 "confidence": r.confidence_score, "source": r.source} for r in rows]

    async def stats(self):
        word_count = len((await self.db.execute(select(BandariWord.id))).scalars().all())
        knowledge_count = len((await self.db.execute(select(LocalKnowledge.id))).scalars().all())
        return {"version": "6.0.0-python", "database_available": True,
                "words": word_count, "knowledge": knowledge_count,
                "features": ["sqlite", "fuzzy-compatible-search", "dialect-detection", "translation", "local-knowledge"],
                "node_dependency": False}

    @staticmethod
    def _word(r: BandariWord):
        return {"id": r.id, "word_standard": r.word_standard, "word_bandari": r.word_bandari,
                "dialect": r.dialect_code, "definition": r.definition, "example": r.example,
                "confidence": r.confidence_score, "data_quality": r.data_quality,
                "region_usage": r.region_usage, "etymology": r.etymology, "cultural_note": r.cultural_note}
