from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PriceSnapshot:
    product: str
    price: float
    turn: int
    inventory: int = 0


@dataclass
class PriceHistory:
    product: str
    snapshots: list[PriceSnapshot] = field(default_factory=list)

    def add(self, snapshot: PriceSnapshot) -> None:
        self.snapshots.append(snapshot)

    def count(self) -> int:
        return len(self.snapshots)

    def current_price(self) -> float | None:
        if not self.snapshots:
            return None
        return float(self.snapshots[-1].price)

    def prices_list(self) -> list[float]:
        return [float(s.price) for s in self.snapshots]


class PriceTracker:
    """Tracks price history for products across turns.

    Records one snapshot per product per turn, in strict turn order.
    """

    def __init__(self, window: int = 20):
        self._window = window
        self._histories: dict[str, PriceHistory] = {}

    def record(self, turn: int, prices: dict[str, int], inventory: dict[str, int]) -> None:
        for product, price in prices.items():
            history = self._histories.setdefault(product, PriceHistory(product=product))
            history.add(
                PriceSnapshot(
                    product=product,
                    price=float(price),
                    turn=turn,
                    inventory=inventory.get(product, 0),
                )
            )
            if history.count() > self._window:
                history.snapshots = history.snapshots[-self._window :]

    def products_tracked(self) -> list[str]:
        return sorted(self._histories.keys())

    def get_history(self, product: str) -> PriceHistory | None:
        return self._histories.get(product)

    def current_prices(self) -> dict[str, float]:
        return {
            product: history.current_price() or 0.0 for product, history in self._histories.items()
        }

    def reset(self) -> None:
        self._histories.clear()
