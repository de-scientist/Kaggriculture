"""Stage 2 — Market Demand Model.

Tracks demand signals observed through market behavior (price changes,
inventory depletion rates) using only current and past observations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DemandSignal:
    """A single demand observation."""

    turn: int
    product: str
    inventory_change: int  # negative = demand exceeded supply
    price_change: float
    sales_volume: int


@dataclass
class DemandHistory:
    """Demand tracking for a single product."""

    product: str
    signals: list[DemandSignal] = field(default_factory=list)

    def add(self, signal: DemandSignal) -> None:
        self.signals.append(signal)

    def recent_signals(self, n: int = 10) -> list[DemandSignal]:
        return self.signals[-n:]

    def demand_trend(self) -> float:
        """Return a trend indicator: positive = increasing demand."""
        if len(self.signals) < 2:
            return 0.0
        recent = self.signals[-5:] if len(self.signals) >= 5 else self.signals
        total_change = sum(s.inventory_change for s in recent)
        return float(total_change) / max(1, len(recent))

    def demand_strength(self) -> float:
        """Normalized demand strength (0–1)."""
        if not self.signals:
            return 0.5
        recent = self.signals[-5:] if len(self.signals) >= 5 else self.signals
        avg_change = sum(s.inventory_change for s in recent) / len(recent)
        return max(0.0, min(1.0, abs(avg_change) / 100.0))


@dataclass
class DemandModel:
    """Tracks demand signals for all products."""

    _histories: dict[str, DemandHistory] = field(default_factory=dict)

    def record(
        self,
        turn: int,
        prev_inventory: dict[str, int],
        curr_inventory: dict[str, int],
        prev_prices: dict[str, int],
        curr_prices: dict[str, int],
        sales: dict[str, int],
    ) -> None:
        """Record demand signals from inventory and price changes."""
        all_products = set(prev_inventory) | set(curr_inventory) | set(curr_prices)
        for product in all_products:
            inv_change = (curr_inventory.get(product, 0)) - (prev_inventory.get(product, 0))
            price_change = float(curr_prices.get(product, 0)) - float(prev_prices.get(product, 0))
            sales_vol = sales.get(product, 0)

            if product not in self._histories:
                self._histories[product] = DemandHistory(product=product)

            self._histories[product].add(
                DemandSignal(
                    turn=turn,
                    product=product,
                    inventory_change=inv_change,
                    price_change=price_change,
                    sales_volume=sales_vol,
                )
            )

    def get(self, product: str) -> DemandHistory | None:
        return self._histories.get(product)

    def demand_trends(self) -> dict[str, float]:
        return {p: h.demand_trend() for p, h in self._histories.items()}

    def demand_strengths(self) -> dict[str, float]:
        return {p: h.demand_strength() for p, h in self._histories.items()}

    def reset(self) -> None:
        self._histories.clear()

    def summary(self) -> dict[str, Any]:
        return {
            "trends": self.demand_trends(),
            "strengths": self.demand_strengths(),
            "products_tracked": list(self._histories.keys()),
        }
