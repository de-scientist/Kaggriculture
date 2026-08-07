"""Optional operation profiling.

Profiling must be **disabled by default in production** (chapter 161).  It is
gated on the ``ENABLE_PROFILING`` feature flag and adds negligible overhead
(a single ``perf_counter`` call) when disabled.

Usage::

    with profile_scope(profiler, "candidate_generation"):
        ...

    @profiled("my_function")
    def f(): ...
"""

from __future__ import annotations

import os
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

try:
    from agent.config import is_feature_enabled
except Exception:  # pragma: no cover - fallback if config not loaded yet

    def is_feature_enabled(flag: str) -> bool:
        return os.environ.get(flag, "false").lower() in ("1", "true", "yes")


_env_flag = os.environ.get("ENABLE_PROFILING", "").lower() in ("1", "true", "yes")
_enabled = _env_flag


def enable(enabled: bool = True) -> None:
    global _enabled
    _enabled = enabled


def is_enabled() -> bool:
    return _enabled or is_feature_enabled("ENABLE_PROFILING")


@dataclass
class ProfileSample:
    operation: str
    duration_ms: float
    attributes: dict[str, Any] = field(default_factory=dict)


class Profiler:
    """Collects timed samples for profiled operations."""

    def __init__(self, enabled: bool | None = None) -> None:
        self._enabled = enabled if enabled is not None else is_enabled()
        self._samples: list[ProfileSample] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    def record(self, operation: str, duration_ms: float, **attributes: Any) -> None:
        if not self._enabled:
            return
        self._samples.append(
            ProfileSample(
                operation=operation,
                duration_ms=round(float(duration_ms), 3),
                attributes=dict(attributes),
            )
        )

    def samples(self) -> list[ProfileSample]:
        return list(self._samples)

    def summary(self) -> dict[str, dict[str, float]]:
        buckets: dict[str, list[float]] = defaultdict(list)
        for s in self._samples:
            buckets[s.operation].append(s.duration_ms)
        result: dict[str, dict[str, float]] = {}
        for op, times in buckets.items():
            result[op] = {
                "count": len(times),
                "total_ms": round(sum(times), 3),
                "avg_ms": round(sum(times) / len(times), 3),
                "min_ms": round(min(times), 3),
                "max_ms": round(max(times), 3),
            }
        return result

    def reset(self) -> None:
        self._samples.clear()


class profile_scope:  # noqa: N801
    """Context manager that profiles a code block when profiling is enabled."""

    def __init__(self, profiler: Profiler, operation: str, **attributes: Any) -> None:
        self._profiler = profiler
        self._operation = operation
        self._attributes = attributes
        self._start: float = 0.0

    def __enter__(self) -> profile_scope:
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._profiler.enabled:
            duration = (time.perf_counter() - self._start) * 1000.0
            self._profiler.record(self._operation, duration, **self._attributes)


def profiled(operation: str, *, profiler: Profiler | None = None) -> Callable[[Callable], Callable]:
    """Decorator that profiles a function when profiling is enabled."""

    def decorator(func: Callable) -> Callable:
        prof = profiler or get_profiler()
        if not prof.enabled:
            return func

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                duration = (time.perf_counter() - start) * 1000.0
                prof.record(operation, duration, func=func.__qualname__)

        wrapper.__wrapped__ = func  # type: ignore[attr-defined]
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


_default_profiler: Profiler | None = None


def get_profiler() -> Profiler:
    global _default_profiler
    if _default_profiler is None:
        _default_profiler = Profiler()
    return _default_profiler


def reset_profiler() -> Profiler:
    global _default_profiler
    _default_profiler = Profiler()
    return _default_profiler
