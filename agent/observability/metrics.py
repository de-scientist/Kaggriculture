"""Runtime metrics collection (chapter 160).

The :class:`MetricsCollector` accumulates cumulative counters and timers that
track the operational health and economic productivity of the agent.  All
metrics are queryable via :meth:`snapshot` and are cumulative across the
lifetime of the process.

Tracked metrics: average decision time, average worker utilization, harvest
count, crop yield, animal productivity, inventory turnover, profit per day,
idle turns, land utilization, and expansion frequency.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

_timer = time.perf_counter


@dataclass
class Counter:
    value: float = 0.0

    def inc(self, by: float = 1.0) -> None:
        self.value += by

    def set(self, value: float) -> None:
        self.value = value


@dataclass
class RateCounter:
    """Tracks a cumulative count and associated sample count for averaging."""

    total: float = 0.0
    count: float = 0.0

    def observe(self, value: float) -> None:
        self.total += value
        self.count += 1

    @property
    def average(self) -> float:
        return self.total / self.count if self.count else 0.0


class MetricsCollector:
    """Thread-safe, cumulative metrics registry."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, Counter] = defaultdict(Counter)
        self._rates: dict[str, RateCounter] = defaultdict(RateCounter)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)

    # -- counters ---------------------------------------------------------
    def increment(self, name: str, by: float = 1.0) -> None:
        with self._lock:
            self._counters[name].inc(by)

    def set_counter(self, name: str, value: float) -> None:
        with self._lock:
            self._counters[name].set(value)

    def counter(self, name: str) -> float:
        with self._lock:
            return self._counters[name].value

    # -- rates / averages -------------------------------------------------
    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._rates[name].observe(value)

    def average(self, name: str) -> float:
        with self._lock:
            rate = self._rates.get(name)
            return rate.average if rate else 0.0

    # -- gauges -----------------------------------------------------------
    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = float(value)

    def gauge(self, name: str) -> float | None:
        with self._lock:
            return self._gauges.get(name)

    # -- histograms -------------------------------------------------------
    def record_value(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms[name].append(float(value))

    def percentile(self, name: str, pct: float) -> float | None:
        with self._lock:
            values = sorted(self._histograms.get(name, []))
        if not values:
            return None
        idx = int((pct / 100.0) * (len(values) - 1))
        return values[idx]

    # -- domain-specific convenience --------------------------------------
    def record_decision_time(self, ms: float) -> None:
        self.observe("decision_time_ms", ms)
        self.record_value("decision_time_ms", ms)

    def record_harvest(self, crop: str, units: float, value: float) -> None:
        self.increment("harvest_count")
        self.increment(f"harvest_count_{crop}", by=units)
        self.increment("crop_yield_total", by=units)
        self.increment("profit_total", by=value)

    def record_animal_product(self, animal: str, units: float, value: float) -> None:
        self.increment("animal_product_count")
        self.increment(f"animal_yield_{animal}", by=units)
        self.increment("profit_total", by=value)

    def record_idle_turn(self) -> None:
        self.increment("idle_turns")

    def record_idle(self, turn: int = 1) -> None:
        self.increment("idle_turns", by=turn)

    def record_land_utilization(self, used: int, total: int) -> None:
        ratio = used / total if total else 0.0
        self.set_gauge("land_utilization_ratio", ratio)

    def record_expansion(self, quadrant: str) -> None:
        self.increment("expansion_count")
        self.increment(f"expansion_{quadrant}")

    def record_worker_utilization(self, busy: int, total: int) -> None:
        ratio = busy / total if total else 0.0
        self.set_gauge("worker_utilization_ratio", ratio)
        self.increment("worker_busy_units", by=busy)
        self.increment("worker_total_units", by=total)

    def record_inventory_turnover(self, items: int) -> None:
        self.observe("inventory_turnover", float(items))

    def record_profit(self, profit: float, day: int | None = None) -> None:
        self.increment("profit_total", by=profit)
        if day is not None:
            self._daily_profit(day, profit)

    def _daily_profit(self, day: int, profit: float) -> None:
        with self._lock:
            bucket = self._rates.setdefault(f"profit_day_{day}", RateCounter())
        bucket.observe(profit)

    def profit_per_day(self) -> dict[int, float]:
        with self._lock:
            return {
                int(k.split("_")[-1]): v.average
                for k, v in self._rates.items()
                if k.startswith("profit_day_")
            }

    # -- snapshot ---------------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            counters = {k: v.value for k, v in self._counters.items()}
            averages = {k: v.average for k, v in self._rates.items()}
            gauges = dict(self._gauges)
            histograms = {
                k: {
                    "count": len(v),
                    "min": min(v) if v else 0.0,
                    "max": max(v) if v else 0.0,
                    "p50": sorted(v)[int(len(v) * 0.5)] if v else 0.0,
                    "p90": sorted(v)[int(len(v) * 0.9)] if v else 0.0,
                    "p99": sorted(v)[int(len(v) * 0.99)] if v else 0.0,
                }
                for k, v in self._histograms.items()
            }
        return {
            "counters": counters,
            "averages": averages,
            "gauges": gauges,
            "histograms": histograms,
            "average_decision_time_ms": averages.get("decision_time_ms", 0.0),
            "total_harvests": counters.get("harvest_count", 0.0),
            "total_profit": counters.get("profit_total", 0.0),
            "idle_turns": counters.get("idle_turns", 0.0),
            "expansion_count": counters.get("expansion_count", 0.0),
        }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._rates.clear()
            self._gauges.clear()
            self._histograms.clear()


_default_collector: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    global _default_collector
    if _default_collector is None:
        _default_collector = MetricsCollector()
    return _default_collector


def reset_metrics() -> MetricsCollector:
    global _default_collector
    _default_collector = MetricsCollector()
    return _default_collector
