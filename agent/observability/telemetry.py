"""Runtime telemetry aggregation (chapter 163).

``Telemetry`` aggregates end-of-turn runtime statistics intended for local
analysis and debugging in Stage 1:

* decision count
* average latency
* longest decision
* failed validations
* strategy usage
* exception counts

Telemetry remains local; future stages may export metrics externally.
"""
from __future__ import annotations

import threading
import time
from collections import Counter
from dataclasses import dataclass

from agent.observability.metrics import MetricsCollector, get_metrics


@dataclass
class TelemetrySnapshot:
    decisions: int
    average_latency_ms: float
    longest_decision_ms: float
    failed_validations: int
    strategy_usage: dict[str, int]
    exception_counts: dict[str, int]
    started_at: float
    uptime_turns: int


class Telemetry:
    """Aggregates runtime statistics across the decision loop."""

    def __init__(self, metrics: MetricsCollector | None = None) -> None:
        self._lock = threading.Lock()
        self._metrics = metrics or get_metrics()
        self._decisions = 0
        self._total_latency = 0.0
        self._longest_latency = 0.0
        self._failed_validations = 0
        self._strategy_usage: Counter = Counter()
        self._exceptions: Counter = Counter()
        self._started_at = time.perf_counter()

    @property
    def metrics(self) -> MetricsCollector:
        return self._metrics

    def record_decision(self, latency_ms: float, strategy: str = "baseline") -> None:
        with self._lock:
            self._decisions += 1
            self._total_latency += latency_ms
            self._longest_latency = max(self._longest_latency, latency_ms)
            self._strategy_usage[strategy] += 1
        self._metrics.record_decision_time(latency_ms)
        self._metrics.increment("decision_count")

    def record_failed_validation(self) -> None:
        with self._lock:
            self._failed_validations += 1
        self._metrics.increment("failed_validations")

    def record_exception(self, exc_type: str) -> None:
        with self._lock:
            self._exceptions[exc_type] += 1
        self._metrics.increment("exception_count")
        self._metrics.increment(f"exception_count_{exc_type}")

    def record_strategy(self, name: str) -> None:
        with self._lock:
            self._strategy_usage[name] += 1

    @property
    def decisions(self) -> int:
        with self._lock:
            return self._decisions

    def average_latency_ms(self) -> float:
        with self._lock:
            if self._decisions == 0:
                return 0.0
            return self._total_latency / self._decisions

    def snapshot(self) -> TelemetrySnapshot:
        with self._lock:
            return TelemetrySnapshot(
                decisions=self._decisions,
                average_latency_ms=round(self._total_latency / self._decisions, 3)
                if self._decisions
                else 0.0,
                longest_decision_ms=round(self._longest_latency, 3),
                failed_validations=self._failed_validations,
                strategy_usage=dict(self._strategy_usage),
                exception_counts=dict(self._exceptions),
                started_at=self._started_at,
                uptime_turns=self._decisions,
            )

    def report(self) -> dict[str, object]:
        snap = self.snapshot()
        return {
            "decisions": snap.decisions,
            "average_latency_ms": snap.average_latency_ms,
            "longest_decision_ms": snap.longest_decision_ms,
            "failed_validations": snap.failed_validations,
            "strategy_usage": snap.strategy_usage,
            "exception_counts": snap.exception_counts,
            "uptime_seconds": round(time.perf_counter() - snap.started_at, 3),
        }

    def reset(self) -> None:
        with self._lock:
            self._decisions = 0
            self._total_latency = 0.0
            self._longest_latency = 0.0
            self._failed_validations = 0
            self._strategy_usage.clear()
            self._exceptions.clear()
            self._started_at = time.perf_counter()
        self._metrics.reset()


_default_telemetry: Telemetry | None = None


def get_telemetry() -> Telemetry:
    global _default_telemetry
    if _default_telemetry is None:
        _default_telemetry = Telemetry()
    return _default_telemetry


def reset_telemetry() -> Telemetry:
    global _default_telemetry
    _default_telemetry = Telemetry()
    return _default_telemetry
