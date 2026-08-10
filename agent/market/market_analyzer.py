from __future__ import annotations

from typing import Any


class MarketAnalyzer:
    """Analyzes market trends and conditions."""

    def __init__(self) -> None:
        self._window: int = 10

    def analyze_trend(
        self,
        snapshots: list[Any],
    ) -> dict[str, Any]:
        if len(snapshots) < 2:
            return {"trend": "unknown", "slope": 0.0, "confidence": 0.5}

        prices = [s.price if hasattr(s, "price") else s for s in snapshots]
        slope = (prices[-1] - prices[0]) / len(prices) if len(prices) > 1 else 0.0
        trending = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        return {"trend": trending, "slope": slope, "confidence": 0.7}

    def detect_regime(
        self,
        history: list[float],
    ) -> str:
        if len(history) < 5:
            return "unknown"
        avg = sum(history[-10:]) / min(10, len(history))
        if avg > 100:
            return "bullish"
        elif avg < 10:
            return "weak"
        return "stable"

    def compute_demand(
        self,
        product: str,
        snapshots: list[Any],
    ) -> float:
        return 0.0

    def compute_supply(
        self,
        product: str,
        snapshots: list[Any],
    ) -> float:
        return 0.0


def analyze_trend(snapshots: list) -> dict:
    analyzer = MarketAnalyzer()
    return analyzer.analyze_trend(snapshots)


def compute_demand(product: str, snapshots: list) -> float:
    analyzer = MarketAnalyzer()
    return analyzer.compute_demand(product, snapshots)


def compute_supply(product: str, snapshots: list) -> float:
    analyzer = MarketAnalyzer()
    return analyzer.compute_supply(product, snapshots)
