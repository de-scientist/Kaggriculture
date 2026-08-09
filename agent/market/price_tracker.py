from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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


class PriceTracker:
    """Tracks price history for products.

    Tracks:
    * Current Price
    * Previous Price
    * Moving Average
    * Price Change
    * Price Change Rate
    * Volatility
    """

    def __init__(self, window: int = 10):
        self._history: dict[str, list[int]] = {}
        self._snapshots: dict[str, PriceHistory] = {}
        self._window = window

    def update(self, product: str, price: int, turn: int = 0) -> None:
        if product not in self._history:
            self._history[product] = []
            self._snapshots[product] = PriceHistory(product=product)
        self._history[product].append(price)
        if len(self._history[product]) > self._window:
            self._history[product] = self._history[product][-self._window:]
        self._snapshots[product].snapshots.append(
            PriceSnapshot(product=product, price=price, turn=turn, timestamp=0.0)
        )

    def get_current_price(self, product: str) -> int | None:
        history = self._history.get(product, [])
        return history[-1] if history else None

    def get_previous_price(self, product: str) -> int | None:
        history = self._history.get(product, [])
        return history[-2] if len(history) >= 2 else None

    def get_moving_average(self, product: str) -> float | None:
        history = self._history.get(product, [])
        if not history:
            return None
        return sum(history) / len(history)

    def get_price_change(self, product: str) -> int:
        current = self.get_current_price(product)
        prev = self.get_previous_price(product)
        if current is None:
            return 0
        return current - (prev or current)

    def get_price_change_rate(self, product: str) -> float:
        current = self.get_current_price(product)
        prev = self.get_previous_price(product)
        if prev is None or prev == 0:
            return 0.0
        return (current - prev) / abs(prev) * 100.0

    def get_volatility(self, product: str) -> float:
        history = self._history.get(product, [])
        if len(history) < 2:
            return 0.0
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        return (variance ** 0.5) / mean if mean > 0 else 0.0

    def get_all_prices(self, product: str) -> list[int]:
        return list(self._history.get(product, []))

    def get_history(self, product: str) -> PriceHistory | None:
        return self._snapshots.get(product)
