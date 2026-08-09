from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DemandHistory:
    product: str
    observations: list[int] = field(default_factory=list)


@dataclass
class DemandSignal:
    product: str
    current_demand: int
    trend: str
    expected_demand: int
    confidence: float


@dataclass
class PriceSnapshot:
    product: str
    price: int
    turn: int
    timestamp: float


@dataclass
class PriceHistory:
    product: str
    snapshots: list[PriceSnapshot] = field(default_factory=list)


class DemandModel:
    """Tracks demand signals where observable."""

    def __init__(self):
        self._current_demand: dict[str, int] = {}
        self._trend: dict[str, str] = {}
        self._expected_demand: dict[str, int] = {}
        self._confidence: dict[str, float] = {}
        self._history: dict[str, DemandHistory] = {}

    def update(self, product: str, demand: int, trend: str, confidence: float) -> None:
        self._current_demand[product] = demand
        self._trend[product] = trend
        self._expected_demand[product] = demand
        self._confidence[product] = confidence
        if product not in self._history:
            self._history[product] = DemandHistory(product=product)
        self._history[product].observations.append(demand)

    def get_current_demand(self, product: str) -> int | None:
        return self._current_demand.get(product)

    def get_trend(self, product: str) -> str | None:
        return self._trend.get(product)

    def get_expected_demand(self, product: str) -> int | None:
        return self._expected_demand.get(product)

    def get_confidence(self, product: str) -> float | None:
        return self._confidence.get(product)

    def classify_demand(self, product: str) -> str | None:
        current = self.get_current_demand(product)
        trend = self.get_trend(product)
        if current is None:
            return None
        if trend == "increasing" or (current > 10 and trend == "stable"):
            return "high"
        elif trend == "decreasing" or (current < 5 and trend == "stable"):
            return "low"
        return "medium"
