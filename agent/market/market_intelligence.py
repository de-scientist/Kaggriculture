from __future__ import annotations

from typing import Any

from agent.market.price_tracker import PriceTracker
from agent.market.price_forecaster import PriceForecaster
from agent.market.demand_model import DemandModel
from agent.market.market_snapshot import MarketSnapshot
from agent.market.market_analyzer import MarketAnalyzer


class MarketIntelligenceEngine:
    """Market intelligence engine for tracking and analyzing market conditions.

    Tracks:
    * Price history
    * Sales history
    * Demand signals
    * Supply signals
    * Price changes
    * Trend
    * Volatility
    """

    def __init__(self):
        self._price_history: dict[str, list[float]] = {}
        self._sales_history: dict[str, list[int]] = {}
        self._demand_signals: dict[str, int] = {}
        self._supply_signals: dict[str, int] = {}
        self._market_regime: dict[str, str] = {}

    def update(
        self,
        turn: int,
        prices: dict[str, int],
        inventory: dict[str, int],
    ) -> None:
        """Update market intelligence with current observation data."""
        for product, price in prices.items():
            self._price_history.setdefault(product, []).append(price)
            if len(self._price_history[product]) > 50:
                self._price_history[product] = self._price_history[product][-50:]
            self._sales_history.setdefault(product, []).append(0)

        for product, count in inventory.items():
            self._supply_signals.setdefault(product, 0)
            self._supply_signals[product] = count

        if self._price_history:
            for product in self._price_history:
                prices_list = self._price_history[product]
                if len(prices_list) >= 5:
                    avg = sum(prices_list[-10:]) / min(10, len(prices_list[-10:]))
                    self._market_regime.setdefault(product, "stable")

    def get_intelligence(
        self,
        product: str,
        current_price: int,
        stock: int,
    ) -> dict[str, Any]:
        """Return market intelligence for a product."""
        history = self._price_history.get(product, [])
        return {
            "current_price": current_price,
            "price_history": history,
            "moving_average": sum(history[-10:]) / min(10, len(history)) if history else current_price,
            "price_change": current_price,
            "price_change_rate": 0.0,
            "volatility": 0.0,
            "is_sell_opportunity": current_price < self._get_floor_price(product),
            "demand_signal": self._demand_signals.get(product, 0),
            "supply_signal": self._supply_signals.get(product, 0),
            "market_regime": self._market_regime.get(product, "stable"),
        }

    def _get_floor_price(self, product: str) -> int:
        return 1

    def classify_regime(self, product: str) -> str:
        """Classify market regime for a product."""
        history = self._price_history.get(product, [])
        if len(history) < 5:
            return "unknown"
        recent = history[-10:]
        avg_recent = sum(recent) / len(recent)
        if len(history) >= 30 and avg_recent > 100:
            return "bullish"
        elif len(history) >= 30 and avg_recent < 10:
            return "weak"
        elif len(history) >= 30 and self._is_volatile(history):
            return "volatile"
        return "stable"

    def _is_volatile(self, history: list[float]) -> bool:
        if len(history) < 5:
            return False
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        return variance > 100

    def get_current_price(self, product: str) -> int:
        history = self._price_history.get(product, [])
        return history[-1] if history else 1