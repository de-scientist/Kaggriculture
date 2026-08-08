"""Stage 2 — Market Intelligence Engine.

Combines price tracking, forecasting, and demand modeling into a
unified market intelligence system.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

from agent.market.demand_model import DemandModel
from agent.market.price_forecaster import PriceForecaster, PriceForecast
from agent.market.price_tracker import PriceHistory, PriceTracker


@dataclass
class MarketIntelligence:
    """Complete market intelligence snapshot."""

    product: str
    current_price: float
    forecast: PriceForecast | None
    demand_trend: float
    demand_strength: float
    inventory: int

    @property
    def is_buy_opportunity(self) -> bool:
        """True if price is below forecast (potential buying opportunity)."""
        if self.forecast is None:
            return False
        return self.current_price <= self.forecast.expected_price * 0.9

    @property
    def is_sell_opportunity(self) -> bool:
        """True if price is above forecast (potential selling opportunity)."""
        if self.forecast is None:
            return True  # Sell when uncertain
        return self.current_price >= self.forecast.expected_price * 1.1

    @property
    def confidence(self) -> float:
        if self.forecast is None:
            return 0.3
        return self.forecast.confidence


@dataclass
class MarketIntelligenceEngine:
    """Central market intelligence aggregator.

    Tracks price history, forecasts prices, and models demand.
    Thread-safe for concurrent access.
    """

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _price_tracker: PriceTracker = field(default_factory=PriceTracker)
    _forecaster: PriceForecaster = field(default_factory=PriceForecaster)
    _demand_model: DemandModel = field(default_factory=DemandModel)
    _prev_inventory: dict[str, int] = field(default_factory=dict)
    _prev_prices: dict[str, int] = field(default_factory=dict)
    _prev_turn: int = 0

    def update(
        self,
        turn: int,
        prices: dict[str, int],
        inventory: dict[str, int],
        sales: dict[str, int] | None = None,
    ) -> None:
        """Record a new market observation."""
        with self._lock:
            sales = sales or {}
            self._price_tracker.record(turn, prices, inventory)

            if self._prev_turn > 0 or self._prev_prices:
                self._demand_model.record(
                    turn=turn,
                    prev_inventory=self._prev_inventory,
                    curr_inventory=inventory,
                    prev_prices=self._prev_prices,
                    curr_prices=prices,
                    sales=sales,
                )

            self._prev_inventory = dict(inventory)
            self._prev_prices = dict(prices)
            self._prev_turn = turn

    def get_intelligence(self, product: str, current_price: float, inventory: int) -> MarketIntelligence:
        """Get market intelligence for a specific product."""
        with self._lock:
            history = self._price_tracker.get_history(product)
            forecast = self._forecaster.forecast(history) if history else None
            demand = self._demand_model.get(product)

            return MarketIntelligence(
                product=product,
                current_price=current_price,
                forecast=forecast,
                demand_trend=demand.demand_trend() if demand else 0.0,
                demand_strength=demand.demand_strength() if demand else 0.5,
                inventory=inventory,
            )

    def get_all_intelligence(
        self, prices: dict[str, int], inventory: dict[str, int]
    ) -> dict[str, MarketIntelligence]:
        """Get market intelligence for all products."""
        with self._lock:
            result: dict[str, MarketIntelligence] = {}
            all_products = set(prices.keys()) | set(inventory.keys())
            for product in all_products:
                price = prices.get(product, 1)
                inv = inventory.get(product, 0)
                result[product] = self.get_intelligence(product, price, inv)
            return result

    def sell_recommendation(self, product: str, current_price: float, inventory: int) -> bool:
        """Determine if now is a good time to sell."""
        intel = self.get_intelligence(product, current_price, inventory)
        if intel.forecast is None:
            return True
        return intel.is_sell_opportunity

    def buy_recommendation(self, product: str, current_price: float, inventory: int) -> bool:
        """Determine if now is a good time to buy seeds/products."""
        intel = self.get_intelligence(product, current_price, inventory)
        if intel.forecast is None:
            return False
        return intel.is_buy_opportunity

    def reset(self) -> None:
        with self._lock:
            self._price_tracker.reset()
            self._demand_model.reset()
            self._prev_inventory.clear()
            self._prev_prices.clear()
            self._prev_turn = 0

    def products_tracked(self) -> list[str]:
        with self._lock:
            return self._price_tracker.products_tracked()
