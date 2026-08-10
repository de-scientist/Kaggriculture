from __future__ import annotations

from dataclasses import dataclass

from agent.market.price_tracker import PriceTracker
from agent.market.price_forecaster import PriceForecast, PriceForecaster
from agent.market.demand_model import DemandModel


@dataclass
class MarketIntelligence:
    """Per-product market intelligence for a single decision point."""

    product: str
    current_price: float
    forecast: PriceForecast | None = None
    demand_trend: float = 0.0
    demand_strength: float = 0.5
    inventory: int = 0

    @property
    def is_sell_opportunity(self) -> bool:
        if self.forecast is None:
            return True
        return self.current_price >= self.forecast.expected_price * (1.0 + self.demand_trend * 0.01)

    @property
    def is_buy_opportunity(self) -> bool:
        if self.forecast is None:
            return False
        return self.current_price < self.forecast.expected_price * (1.0 - self.demand_trend * 0.01)

    @property
    def confidence(self) -> float:
        if self.forecast is None:
            return 0.3
        return self.forecast.confidence


class MarketIntelligenceEngine:
    """Market intelligence engine for tracking and analyzing market conditions.

    Only observes data up to the current turn; forecasts never use future data.
    """

    def __init__(self):
        self._price_tracker = PriceTracker()
        self._price_forecaster = PriceForecaster()
        self._demand_model = DemandModel()
        self._last_prices: dict[str, float] = {}
        self._last_inventory: dict[str, int] = {}

    def update(
        self,
        turn: int,
        prices: dict[str, int],
        inventory: dict[str, int],
    ) -> None:
        self._price_tracker.record(turn=turn, prices=prices, inventory=inventory)
        if self._last_inventory:
            self._demand_model.record(
                turn=turn,
                prev_inventory=self._last_inventory,
                curr_inventory=inventory,
                prev_prices=self._last_prices,
                curr_prices=prices,
                sales={},
            )
        self._last_prices = {product: float(price) for product, price in prices.items()}
        self._last_inventory = dict(inventory)

    def get_intelligence(self, product: str, current_price: int, stock: int = 0) -> MarketIntelligence:
        history = self._price_tracker.get_history(product)
        forecast = self._price_forecaster.forecast(history) if history else None
        demand_trend = 0.0
        demand = self._demand_model.get(product)
        if demand is not None:
            demand_trend = demand.demand_trend()
        return MarketIntelligence(
            product=product,
            current_price=float(current_price),
            forecast=forecast,
            demand_trend=demand_trend,
            demand_strength=0.5,
            inventory=stock,
        )

    def get_all_intelligence(
        self,
        prices: dict[str, int],
        inventory: dict[str, int],
    ) -> dict[str, MarketIntelligence]:
        return {
            product: self.get_intelligence(product, price, inventory.get(product, 0))
            for product, price in prices.items()
        }

    def sell_recommendation(self, product: str, current_price: int, quantity: int) -> bool:
        return self.get_intelligence(product, current_price).is_sell_opportunity and quantity > 0

    def buy_recommendation(self, product: str, current_price: int, quantity: int) -> bool:
        return self.get_intelligence(product, current_price).is_buy_opportunity and quantity > 0

    def products_tracked(self) -> list[str]:
        return self._price_tracker.products_tracked()

    def get_forecast(self, product: str) -> PriceForecast | None:
        history = self._price_tracker.get_history(product)
        if history is None:
            return None
        return self._price_forecaster.forecast(history)

    def get_current_price(self, product: str) -> int:
        history = self._price_tracker.get_history(product)
        if history is None or history.current_price() is None:
            return 1
        return int(history.current_price())

    def reset(self) -> None:
        self._price_tracker.reset()
        self._demand_model.reset()
        self._last_prices = {}
        self._last_inventory = {}
