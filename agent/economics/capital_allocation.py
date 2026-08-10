from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CapitalAllocation:
    category: str
    amount: float
    expected_roi: float
    payback_turns: float
    confidence: float
    description: str = ""


class CapitalAllocator:
    """Allocates cash toward the highest expected strategic value.

    Allocates capital among: seeds, animals, feed, fertilizer, workers, land, or reserve.
    """

    def __init__(
        self,
        min_cash_reserve: float = 500.0,
        land_costs: dict[str, int] | None = None,
    ) -> None:
        self.min_cash_reserve = min_cash_reserve
        self.land_costs: dict[str, int] = land_costs or {"NE": 1000, "SW": 2000, "SE": 4000}
        self._logger = None

    def allocate(
        self,
        available_cash: float,
        opportunities: list[CapitalAllocation],
    ) -> list[CapitalAllocation]:
        """Rank opportunities by expected ROI and allocate capital."""
        reserve = self.min_cash_reserve
        spendable = max(0.0, available_cash - reserve)

        ranked = sorted(
            opportunities,
            key=lambda opp: (-opp.expected_roi, -opp.confidence, opp.category),
        )

        selected: list[CapitalAllocation] = []
        allocated = 0.0
        for opp in ranked:
            if allocated + opp.amount <= spendable:
                selected.append(opp)
                allocated += opp.amount
            if allocated >= spendable:
                break

        return selected

    def land_allocation(
        self,
        cash: float,
        expected_profit_per_turn: float,
        remaining_turns: int,
    ) -> CapitalAllocation | None:
        """Evaluate land purchase as a capital allocation."""
        if expected_profit_per_turn <= 0 or remaining_turns <= 0:
            return None

        for quadrant in ("NE", "SW", "SE"):
            cost = float(self.land_costs.get(quadrant, 0))
            if cost <= 0 or cash < cost:
                continue

            if expected_profit_per_turn > 0:
                payback = cost / expected_profit_per_turn
            else:
                payback = float("inf")
            if payback > remaining_turns:
                continue

            roi = (expected_profit_per_turn * remaining_turns - cost) / cost * 100.0
            confidence = min(1.0, remaining_turns / (payback + 1))

            return CapitalAllocation(
                category=f"land_{quadrant}",
                amount=cost,
                expected_roi=roi,
                payback_turns=payback,
                confidence=confidence,
                description=f"Unlock {quadrant} quadrant for ${cost:.0f}, "
                f"payback in {payback:.1f} turns",
            )
        return None
