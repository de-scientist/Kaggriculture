from __future__ import annotations

from typing import Any

from agent.market.price_tracker import PriceTracker, PriceHistory, PriceSnapshot
from agent.market.price_forecaster import PriceForecaster, PriceForecast
from agent.market.demand_model import DemandModel, DemandSignal, DemandHistory
from agent.market.market_snapshot import MarketSnapshot
from agent.market.market_analyzer import MarketAnalyzer


class MarketIntelligence:
    """Container for market intelligence."""

    def __init__(self):
        self.prices: dict[str, int] = {}
        self.inventory: dict[str, int] = {}
        self.price_history: dict[str, list[float]] = {}
        self.demand_signals: dict[str, int] = {}
        self.supply_signals: dict[str, int] = {}
        self.forecasts: dict[str, PriceForecast] = {}
        self.regimes: dict[str, str] = {}


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
        self._price_tracker = PriceTracker()
        self._price_forecaster = PriceForecaster()
        self._demand_model = DemandModel()
        self._market_analyzer = MarketAnalyzer()
        self._price_history: dict[str, list[float]] = {}
        self._sales_history: dict[str, list[int]] = {}
        self._demand_signals: dict[str, int] = {}
        self._supply_signals: dict[str, int] = {}
        self._market_regime: dict[str, str] = {}
        self._snapshots: list[MarketSnapshot] = []

    def update(
        self,
        turn: int,
        prices: dict[str, int],
        inventory: dict[str, int],
    ) -> None:
        """Update market intelligence with current observation data."""
        for product, price in prices.items():
            self._price_tracker.update(product, price, turn)
            self._price_history.setdefault(product, []).append(float(price))
            if len(self._price_history[product]) > 50:
                self._price_history[product] = self._price_history[product][-50:]
            self._sales_history.setdefault(product, []).append(0)

        if prices:
            self._snapshots.append(
                MarketSnapshot(
                    timestamp=turn,
                    inventory=dict(inventory),
                    prices=dict(prices),
                )
            )
            if len(self._snapshots) > 50:
                self._snapshots = self._snapshots[-50:]

        for product, count in inventory.items():
            self._supply_signals.setdefault(product, 0)
            self._supply_signals[product] = count

        if self._price_history:
            for product in self._price_history:
                prices_list = self._price_history[product]
                if len(prices_list) >= 5:
                    avg = sum(prices_list[-10:]) / min(10, len(prices_list[-10:]))
                    regime = self._market_analyzer.detect_regime(prices_list)
                    self._market_regime[product] = regime

        # Update forecasts
        forecasts = self._price_forecaster.forecast(
            current_prices=prices,
            history=self._price_history,
        )
        self._forecasts = forecasts

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
            "moving_average": sum(history[-10:]) / min(10, len(history[-10:])) if history else float(current_price),
            "price_change": self._price_tracker.get_price_change(product) or 0,
            "price_change_rate": self._price_tracker.get_price_change_rate(product),
            "volatility": self._price_tracker.get_volatility(product),
            "is_sell_opportunity": self._is_sell_opportunity(product, current_price),
            "demand_signal": self._demand_signals.get(product, 0),
            "supply_signal": self._supply_signals.get(product, 0),
            "market_regime": self._market_regime.get(product, "stable"),
            "forecast": self._forecasts.get(product),
        }

    def _is_sell_opportunity(
        self,
        product: str,
        current_price: int,
    ) -> bool:
        history = self._price_history.get(product, [])
        if len(history) < 5:
            return current_price > 0
        moving_avg = sum(history[-5:]) / len(history[-5:])
        return current_price > moving_avg

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
        return self._price_tracker.get_current_price(product) or 1

    def get_forecast(self, product: str) -> PriceForecast | None:
        return self._forecasts.get(product) if hasattr(self, "_forecasts") else None

    def __init_post_init__(self):
        if not hasattr(self, "_forecasts"):
            self._forecasts: dict[str, PriceForecast] = {}
