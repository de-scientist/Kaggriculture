"""Stage 2 — Price Tracking.

Tracks historical market prices for each product, enabling trend
analysis and forecasting. Uses only information observable at the
current turn (no future leakage).
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class PriceSnapshot:
    """A single price observation at a point in time."""

    turn: int
    product: str
    price: float
    inventory: int


@dataclass
class PriceHistory:
    """Historical price observations for a single product."""

    product: str
    prices: deque = field(default_factory=lambda: deque(maxlen=50))
    inventory_history: deque = field(default_factory=lambda: deque(maxlen=50))

    def add(self, snapshot: PriceSnapshot) -> None:
        self.prices.append(snapshot)
        self.inventory_history.append(snapshot.inventory)

    def current_price(self) -> float | None:
        if not self.prices:
            return None
        return self.prices[-1].price

    def prices_list(self) -> list[float]:
        return [s.price for s in self.prices]

    def inventory_list(self) -> list[int]:
        return [s.inventory for s in self.prices]

    def count(self) -> int:
        return len(self.prices)


@dataclass
class PriceTracker:
    """Tracks price history for all market products."""

    _histories: dict[str, PriceHistory] = field(default_factory=dict)

    def record(self, turn: int, prices: dict[str, int], inventory: dict[str, int]) -> None:
        """Record a price observation for the current turn."""
        for product, price in prices.items():
            if product not in self._histories:
                self._histories[product] = PriceHistory(product=product)
            inv = inventory.get(product, 0)
            self._histories[product].add(
                PriceSnapshot(turn=turn, product=product, price=float(price), inventory=inv)
            )

    def get_history(self, product: str) -> PriceHistory | None:
        return self._histories.get(product)

    def current_prices(self) -> dict[str, float | None]:
        return {p: h.current_price() for p, h in self._histories.items()}

    def products_tracked(self) -> list[str]:
        return list(self._histories.keys())

    def reset(self) -> None:
        self._histories.clear()
