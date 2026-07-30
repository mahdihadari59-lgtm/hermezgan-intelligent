"""
providers/__init__.py

Shared base class for all HDP providers.

Design goals (consistent with existing HDP conventions):
- stdlib-first: HTTP calls use urllib in a thread executor so no new
  third-party dependency is required on Termux. If `httpx` is already
  a project dependency, swap `_http_get`/`_http_post` for an async client.
- Each provider exposes a uniform async `query(payload: dict) -> dict`
  and a `health() -> bool`, so CopilotGateway can treat all providers
  identically.
- A lightweight 3-state circuit breaker (closed/open/half-open) mirrors
  the pattern already used in engine_adapter.py, so provider failures
  degrade gracefully instead of cascading.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("hdp.providers")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    failures: int = 0
    opened_at: Optional[float] = None

    def on_success(self) -> None:
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None

    def on_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.monotonic()

    def allow_request(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if self.opened_at and (time.monotonic() - self.opened_at) >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False
        # HALF_OPEN: allow a single probe request through
        return True


@dataclass
class ProviderMetrics:
    calls: int = 0
    errors: int = 0
    total_latency_ms: float = 0.0

    def record(self, latency_ms: float, ok: bool) -> None:
        self.calls += 1
        self.total_latency_ms += latency_ms
        if not ok:
            self.errors += 1

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.calls if self.calls else 0.0


class ProviderError(RuntimeError):
    """Raised when a provider cannot fulfil a request (breaker open, timeout, bad response)."""


class BaseProvider:
    """
    Common contract for all providers used by CopilotGateway.

    Subclasses implement `_execute(payload)` with their real logic;
    `query()` wraps it with the circuit breaker + metrics + timeout.
    """

    name: str = "base"

    def __init__(self, timeout: float = 5.0, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.timeout = timeout
        self.breaker = CircuitBreaker(failure_threshold=failure_threshold, recovery_timeout=recovery_timeout)
        self.metrics = ProviderMetrics()

    async def query(self, payload: dict) -> dict:
        if not self.breaker.allow_request():
            raise ProviderError(f"{self.name}: circuit open, skipping call")

        start = time.monotonic()
        try:
            result = await asyncio.wait_for(self._execute(payload), timeout=self.timeout)
            self.breaker.on_success()
            self.metrics.record((time.monotonic() - start) * 1000, ok=True)
            return result
        except Exception as exc:  # noqa: BLE001 - provider boundary, must not raise raw
            self.breaker.on_failure()
            self.metrics.record((time.monotonic() - start) * 1000, ok=False)
            logger.warning("%s provider failed: %s", self.name, exc)
            raise ProviderError(f"{self.name}: {exc}") from exc

    async def _execute(self, payload: dict) -> dict:
        raise NotImplementedError

    async def health(self) -> bool:
        try:
            await self.query({"__health__": True})
            return True
        except ProviderError:
            return False

    # --- shared stdlib HTTP helpers -------------------------------------

    @staticmethod
    def _blocking_http_post(url: str, body: dict, timeout: float) -> dict:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    @staticmethod
    def _blocking_http_get(url: str, timeout: float) -> dict:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    async def _http_post(self, url: str, body: dict) -> dict:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._blocking_http_post, url, body, self.timeout)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"HTTP POST {url} failed: {exc}") from exc

    async def _http_get(self, url: str) -> dict:
        loop = asyncio.get_running_loop()
        try:
            return await loop.run_in_executor(None, self._blocking_http_get, url, self.timeout)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise ProviderError(f"HTTP GET {url} failed: {exc}") from exc
