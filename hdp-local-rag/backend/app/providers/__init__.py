from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
import time


@dataclass
class BaseProvider:
    timeout_seconds: float = 10.0
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "calls": 0,
        "errors": 0,
        "last_latency_ms": 0,
    })

    def _mark_call(self, started_at: float) -> None:
        self.metrics["calls"] += 1
        self.metrics["last_latency_ms"] = int((time.time() - started_at) * 1000)

    def _mark_error(self) -> None:
        self.metrics["errors"] += 1
