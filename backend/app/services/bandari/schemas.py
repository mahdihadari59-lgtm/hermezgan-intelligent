from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass(slots=True)
class TranslationResult:
    translation: str
    normalized_text: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class DetectionResult:
    dialect: str
    confidence: float
    language: str = "fa"
    raw: dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True)
class MultilingualTranslationResult:
    results: list[dict[str, Any]]
    raw: dict[str, Any] = field(default_factory=dict)
