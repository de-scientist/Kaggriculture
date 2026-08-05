from __future__ import annotations

from agent.domain.prices import Price


class Market:
    __slots__ = ("_history", "_inventory", "_prices")

    def __init__(
        self,
        inventory: dict[str, int] | None = None,
        prices: dict[str, int] | None = None,
    ) -> None:
        self._inventory = dict(inventory or {})
        self._prices = dict(prices or {})
        self._history: list[dict[str, int]] = []

    @property
    def inventory(self) -> dict[str, int]:
        return dict(self._inventory)

    @property
    def prices(self) -> dict[str, int]:
        return dict(self._prices)

    @property
    def history(self) -> list[dict[str, int]]:
        return list(self._history)

    def current_price(self, product: str) -> Price:
        value = self._prices.get(product, 1)
        return Price(value=value)

    def update_price(self, product: str, new_price: int) -> Market:
        if new_price < 1:
            raise ValueError("Price cannot be below 1")
        new_prices = dict(self._prices)
        old_price = new_prices.get(product, 1)
        new_prices[product] = new_price
        m = Market(inventory=self._inventory, prices=new_prices)
        m._history = list(self._history)
        m._history.append({product: old_price})
        return m

    def update_inventory(self, product: str, delta: int) -> Market:
        new_inv = dict(self._inventory)
        new_inv[product] = new_inv.get(product, 0) + delta
        if new_inv[product] < 0:
            new_inv[product] = 0
        return Market(inventory=new_inv, prices=self._prices)

    def estimate_roi(self, product: str, cost: float, expected_sale_price: float) -> float:
        if cost <= 0:
            return 0.0
        return (expected_sale_price - cost) / cost

    def __repr__(self) -> str:
        return f"Market(inv={self._inventory}, prices={self._prices})"
