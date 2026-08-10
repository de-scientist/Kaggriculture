from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DemandSignal:
    turn: int
    product: str
    inventory_change: int
    price_change: float
    sales_volume: int = 0


@dataclass
class DemandHistory:
    product: str
    signals: list[DemandSignal] = field(default_factory=list)

    def add(self, signal: DemandSignal) -> None:
        self.signals.append(signal)

    def count(self) -> int:
        return len(self.signals)

    def recent_signals(self, n: int) -> list[DemandSignal]:
        return self.signals[-n:]

    def demand_trend(self) -> float:
        if not self.signals:
            return 0.0
        return sum(s.inventory_change for s in self.signals)


class DemandModel:
    """Tracks demand signals derived from observed inventory changes.

    Records only observations that have already happened (no future data).
    """

    def __init__(self) -> None:
        self._history: dict[str, DemandHistory] = {}

    def record(
        self,
        turn: int,
        prev_inventory: dict[str, int],
        curr_inventory: dict[str, int],
        prev_prices: dict[str, int],
        curr_prices: dict[str, int],
        sales: dict[str, int],
    ) -> None:
        for product in curr_inventory:
            inventory_change = curr_inventory.get(product, 0) - prev_inventory.get(product, 0)
            price_change = float(curr_prices.get(product, 0)) - float(prev_prices.get(product, 0))
            sales_volume = int(sales.get(product, 0))
            history = self._history.setdefault(product, DemandHistory(product=product))
            history.add(
                DemandSignal(
                    turn=turn,
                    product=product,
                    inventory_change=inventory_change,
                    price_change=price_change,
                    sales_volume=sales_volume,
                )
            )

    def get(self, product: str) -> DemandHistory | None:
        return self._history.get(product)

    def products_tracked(self) -> list[str]:
        return sorted(self._history.keys())

    def reset(self) -> None:
        self._history.clear()

    def summary(self) -> dict[str, Any]:
        trends: dict[str, float] = {p: h.demand_trend() for p, h in self._history.items()}
        strengths: dict[str, float] = {
            p: max(0.0, min(1.0, 1.0 - abs(h.demand_trend()) / 50.0))
            for p, h in self._history.items()
        }
        return {
            "trends": trends,
            "strengths": strengths,
            "products_tracked": sorted(self._history.keys()),
        }
