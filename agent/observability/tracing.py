"""Distributed tracing for decisions.

Every decision turn receives a *trace* with a unique, deterministic
``decision_id`` (``d-{step}``) and a per-episode ``correlation_id``
(``c-{seed}-{player}``).  Each phase of the decision pipeline — observation,
candidate generation, validation, strategy evaluation, serialization — is
recorded as a :class:`Span` so that the complete path from observation to
submitted action is reconstructable (see chapter 162).

IDs are derived from the step/seed so that, with unchanged configuration, the
same observation produces identical traces (deterministic debugging).
"""
from __future__ import annotations

import contextvars
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

_NANO = 1_000_000.0


@dataclass
class Span:
    """A timed, attributed segment of a decision trace."""

    name: str
    start_ms: float
    end_ms: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    parent: str | None = None

    @property
    def duration_ms(self) -> float:
        return max(0.0, self.end_ms - self.start_ms)

    def finish(self, end_ms: float | None = None) -> None:
        self.end_ms = end_ms if end_ms is not None else _now_ms()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 3),
            "attributes": dict(self.attributes),
        }


@dataclass
class Trace:
    """A complete trace for one decision turn."""

    correlation_id: str
    decision_id: str
    step: int
    day: int
    player: int
    strategy: str
    spans: list[Span] = field(default_factory=list)

    @property
    def total_duration_ms(self) -> float:
        return sum(s.duration_ms for s in self.spans)

    def add_span(self, span: Span) -> Span:
        self.spans.append(span)
        return span

    def to_dict(self) -> dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "decision_id": self.decision_id,
            "step": self.step,
            "day": self.day,
            "player": self.player,
            "strategy": self.strategy,
            "total_duration_ms": round(self.total_duration_ms, 3),
            "spans": [s.to_dict() for s in self.spans],
        }


def _now_ms() -> float:
    return time.perf_counter() * 1000.0


def make_correlation_id(seed: int | None, player: int) -> str:
    """Deterministic correlation id for an episode+player pair."""
    key = f"{seed or 'none'}-{player}"
    digest = hashlib.sha256(key.encode()).hexdigest()[:8]
    return f"c-{digest}"


def make_decision_id(step: int) -> str:
    """Deterministic, unique-per-turn decision id."""
    return f"d-{step}"


class Tracer:
    """Creates and manages decision traces and their spans."""

    def __init__(self, correlation_id: str | None = None) -> None:
        self._correlation_id = correlation_id

    def start_trace(
        self,
        *,
        step: int,
        day: int,
        player: int,
        strategy: str = "baseline",
        correlation_id: str | None = None,
    ) -> Trace:
        cid = correlation_id or self._correlation_id or make_correlation_id(None, player)
        return Trace(
            correlation_id=cid,
            decision_id=make_decision_id(step),
            step=step,
            day=day,
            player=player,
            strategy=strategy,
        )

    @staticmethod
    def start_span(name: str, **attributes: Any) -> Span:
        return Span(name=name, start_ms=_now_ms(), attributes=dict(attributes))

    def set_correlation_id(self, cid: str) -> None:
        self._correlation_id = cid

    @property
    def correlation_id(self) -> str | None:
        return self._correlation_id


_ACTIVE_TRACE: contextvars.ContextVar[Trace | None] = contextvars.ContextVar(
    "_kaggriculture_active_trace", default=None
)


def set_active_trace(trace: Trace | None) -> None:
    _ACTIVE_TRACE.set(trace)


def get_active_trace() -> Trace | None:
    return _ACTIVE_TRACE.get()


class trace_scope:
    """Context manager that pushes a :class:`Trace` onto the active-trace slot."""

    def __init__(self, tracer: Tracer, trace: Trace) -> None:
        self._tracer = tracer
        self._trace = trace
        self._token: contextvars.Token = None  # type: ignore[assignment]

    def __enter__(self) -> Trace:
        self._token = _ACTIVE_TRACE.set(self._trace)
        return self._trace

    def __exit__(self, exc_type, exc, tb) -> None:
        _ACTIVE_TRACE.reset(self._token)
        self._token = None


_default: Tracer | None = None


def get_default_tracer() -> Tracer:
    global _default
    if _default is None:
        _default = Tracer()
    return _default


def reset_default_tracer(correlation_id: str | None = None) -> Tracer:
    global _default
    _default = Tracer(correlation_id)
    return _default
