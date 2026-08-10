from __future__ import annotations

from dataclasses import dataclass

LAND_COSTS: dict[str, float] = {
    "NE": 1000.0,
    "SW": 2000.0,
    "SE": 4000.0,
}


@dataclass
class LandInvestment:
    quadrant: str
    cost: float
    expected_additional_profit: float
    payback_turns: float
    roi: float
    remaining_turns: int
    can_afford: bool
    confidence: float
    reason: str = ""

    @property
    def is_viable(self) -> bool:
        return self.can_afford and self.payback_turns <= self.remaining_turns


class LandOptimizer:
    """Evaluates land expansion investment.

    For every potential expansion:
    * Purchase Cost
    * Additional Capacity
    * Expected Profit
    * Payback Period
    * Remaining Turns
    """

    def __init__(self) -> None:
        self._land_data: dict[str, dict[str, float]] = {}

    def evaluate_expansion(
        self,
        available_cash: float,
        unlocked_quadrants: list[str],
        remaining_turns: int,
        farm_profit_per_turn: float,
        tile_count: int,
    ) -> list[LandInvestment]:
        results: list[LandInvestment] = []
        for quadrant, cost in LAND_COSTS.items():
            if quadrant in unlocked_quadrants:
                continue
            result = self._evaluate_quadrant(
                quadrant=quadrant,
                cost=cost,
                available_cash=available_cash,
                remaining_turns=remaining_turns,
                farm_profit_per_turn=farm_profit_per_turn,
            )
            if result is not None:
                results.append(result)
        results.sort(key=lambda r: (r.cost, r.quadrant))
        return results

    def next_best(
        self,
        available_cash: float,
        unlocked_quadrants: list[str],
        remaining_turns: int,
        farm_profit_per_turn: float,
        tile_count: int,
    ) -> LandInvestment | None:
        candidates = self.evaluate_expansion(
            available_cash=available_cash,
            unlocked_quadrants=unlocked_quadrants,
            remaining_turns=remaining_turns,
            farm_profit_per_turn=farm_profit_per_turn,
            tile_count=tile_count,
        )
        if not candidates:
            return None
        return min(candidates, key=lambda r: r.cost)

    def _get_land_cost(self, quadrant: str) -> float:
        return LAND_COSTS.get(quadrant, 0.0)

    def _evaluate_quadrant(
        self,
        quadrant: str,
        cost: float,
        available_cash: float,
        remaining_turns: int,
        farm_profit_per_turn: float,
    ) -> LandInvestment | None:
        if cost > available_cash:
            return None
        expected_additional_profit = max(farm_profit_per_turn, 0.0)
        if expected_additional_profit <= 0:
            return None
        payback_turns = cost / expected_additional_profit
        roi = (expected_additional_profit * remaining_turns) / cost
        confidence = min(1.0, remaining_turns / max(payback_turns, 1.0))
        return LandInvestment(
            quadrant=quadrant,
            cost=cost,
            expected_additional_profit=expected_additional_profit,
            payback_turns=payback_turns,
            roi=roi,
            remaining_turns=remaining_turns,
            can_afford=True,
            confidence=confidence,
            reason=(
                f"Expected {expected_additional_profit:.1f}/turn, payback {payback_turns:.1f} turns"
            ),
        )

    def set_land_data(self, land_type: str, data: dict[str, float]) -> None:
        self._land_data[land_type] = data
