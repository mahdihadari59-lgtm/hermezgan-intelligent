#!/usr/bin/env python3
"""
hdp/engines/ai/registry/registry.py
===================================================
ارتقای رجیستری موجود - نه جایگزینی. امضای جدید:

    registry.register(kind, name, engine)

اما امضای قدیمی هم همچنان کار می‌کند (backward-compatible)، تا کد
فعلی که هنوز register(name, engine) صدا می‌زند فوراً خراب نشود:

    registry.register(name, engine)   # فرض می‌شود kind=EngineKind.SEARCH
                                       # (چون بیشترین استفاده قدیمی برای
                                       #  موتورهای جستجو بوده) - یک بار
                                       # DeprecationWarning چاپ می‌کند.

نگهداری بر اساس نوع موتور (طبق درخواست):
    INTENT, SEARCH, RANKER, EXPERT, ANSWER

فقط stdlib.
"""

import asyncio
import logging
import warnings
from dataclasses import dataclass
from typing import Any, Optional, Union

from engine.contracts import EngineKind, MULTI_INSTANCE_KINDS

logger = logging.getLogger("hdp.registry")


@dataclass
class RegisteredEngine:
    kind: EngineKind
    name: str
    instance: Any
    version: str = "1.0.0"


class Registry:
    """
    نگهداری موتورها بر اساس EngineKind. برای انواع تک‌نمونه‌ای
    (INTENT/RANKER/EXPERT/ANSWER) فقط یک نمونه فعال مجاز است. برای
    SEARCH (طبق MULTI_INSTANCE_KINDS در contracts.py)، چند نمونه هم‌زمان
    مجازند و با name از هم تفکیک می‌شوند.
    """

    def __init__(self):
        self._single: dict[EngineKind, RegisteredEngine] = {}
        self._multi: dict[EngineKind, dict[str, RegisteredEngine]] = {
            kind: {} for kind in MULTI_INSTANCE_KINDS
        }

    # ------------------------------------------------------------------
    def register(self, *args, version: str = "1.0.0", name: Optional[str] = None):
        """
        دو امضا پشتیبانی می‌شود:
          register(kind: EngineKind, name: str, engine)   <- امضای جدید و توصیه‌شده
          register(name: str, engine)                      <- امضای قدیمی (deprecated)
        """
        if len(args) == 3:
            kind, entry_name, engine = args
        elif len(args) == 2:
            first, engine = args
            if isinstance(first, EngineKind):
                kind = first
                entry_name = name or getattr(engine, "name", kind.value)
            else:
                warnings.warn(
                    "Registry.register(name, engine) قدیمی است؛ به "
                    "Registry.register(EngineKind.SEARCH, name, engine) مهاجرت کنید. "
                    "فرض پیش‌فرض: kind=EngineKind.SEARCH.",
                    DeprecationWarning, stacklevel=2,
                )
                kind = EngineKind.SEARCH
                entry_name = first
        else:
            raise TypeError(
                "Registry.register() باید با (kind, name, engine) یا (name, engine) "
                f"صدا زده شود؛ {len(args)} آرگومان دریافت شد."
            )

        entry = RegisteredEngine(kind=kind, name=entry_name, instance=engine, version=version)

        if kind in MULTI_INSTANCE_KINDS:
            if entry_name in self._multi[kind]:
                logger.warning("موتور '%s/%s' از قبل ثبت شده بود؛ جایگزین شد.", kind.value, entry_name)
            self._multi[kind][entry_name] = entry
        else:
            if kind in self._single:
                logger.warning("موتور '%s' از قبل ثبت شده بود؛ جایگزین شد.", kind.value)
            self._single[kind] = entry

        logger.info("ثبت شد: kind=%s name=%s version=%s", kind.value, entry_name, version)
        return self

    # ------------------------------------------------------------------
    def get(self, kind: EngineKind, name: Optional[str] = None) -> Any:
        """
        get(EngineKind.INTENT)                -> نمونه تک (خطا اگر ثبت نشده)
        get(EngineKind.SEARCH, "fts")         -> نمونه خاص از میان چندنمونه‌ای‌ها
        """
        if kind in MULTI_INSTANCE_KINDS:
            if name is None:
                raise KeyError(f"برای نوع چندنمونه‌ای '{kind.value}' باید name مشخص شود.")
            bucket = self._multi[kind]
            if name not in bucket:
                raise KeyError(f"موتور '{kind.value}/{name}' ثبت نشده است.")
            return bucket[name].instance

        if kind not in self._single:
            raise KeyError(f"موتور '{kind.value}' ثبت نشده است.")
        return self._single[kind].instance

    def get_all(self, kind: EngineKind) -> dict[str, Any]:
        """همه نمونه‌های یک نوع چندنمونه‌ای (مثلاً همه موتورهای SEARCH)."""
        if kind not in MULTI_INSTANCE_KINDS:
            # برای یکنواختی، حتی انواع تک‌نمونه‌ای هم به شکل dict برمی‌گردند
            if kind in self._single:
                return {self._single[kind].name: self._single[kind].instance}
            return {}
        return {name: e.instance for name, e in self._multi[kind].items()}

    def has(self, kind: EngineKind, name: Optional[str] = None) -> bool:
        if kind in MULTI_INSTANCE_KINDS:
            if name is None:
                return bool(self._multi[kind])
            return name in self._multi[kind]
        return kind in self._single

    def get_version(self, kind: EngineKind, name: Optional[str] = None) -> Optional[str]:
        if kind in MULTI_INSTANCE_KINDS:
            entry = self._multi[kind].get(name) if name else None
            return entry.version if entry else None
        entry = self._single.get(kind)
        return entry.version if entry else None

    # ------------------------------------------------------------------
    async def health_check(self, timeout_s: float = 2.0) -> dict[str, str]:
        report: dict[str, str] = {}

        async def check_one(key: str, engine: Any):
            if hasattr(engine, "health") and callable(engine.health):
                try:
                    await asyncio.wait_for(engine.health(), timeout=timeout_s)
                    report[key] = "healthy"
                except asyncio.TimeoutError:
                    report[key] = "timeout"
                except Exception as e:  # noqa: BLE001
                    report[key] = f"error: {e}"
            else:
                report[key] = "registered_only"

        tasks = [check_one(e.kind.value, e.instance) for e in self._single.values()]
        for kind, bucket in self._multi.items():
            for name, e in bucket.items():
                tasks.append(check_one(f"{kind.value}/{name}", e.instance))
        await asyncio.gather(*tasks)
        return report

    def summary(self) -> str:
        lines = ["=== Registry ==="]
        for kind, entry in self._single.items():
            lines.append(f"  {kind.value:10s} -> {type(entry.instance).__name__} (v{entry.version})")
        for kind, bucket in self._multi.items():
            for name, entry in bucket.items():
                lines.append(f"  {kind.value + '/' + name:20s} -> {type(entry.instance).__name__} (v{entry.version})")
        return "\n".join(lines)


# نگه‌داشتن نام قدیمی به‌عنوان alias، برای import کدهای موجود که
# "from hdp.engines.ai.registry.registry import EngineRegistry" دارند.
EngineRegistry = Registry

