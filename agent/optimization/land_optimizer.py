from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LandInvestment:
    quadrant: str
    cost: float
    additional_capacity: int
    expected_revenue_per_turn: float
    expected_profit_per_turn: float
    remaining_turns: int
    roi: float
    payback_turns: float
    confidence: float


class LandOptimizer:
    """Evaluates land expansion investment.

    For every potential expansion:
    * Purchase Cost
    * Additional Capacity
    * Expected Revenue
    * Expected Profit
    * Time to Utilize
    * Worker Requirements
    * Payback Period
    * Remaining Turns
    """

    def __init__(self):
        self._land_data = {}

    def evaluate_expansion(
        self,
        available_cash: float,
        unlocked_quadrants: list[str],
        remaining_turns: int,
        farm_profit_per_turn: float,
        tile_count: int,
    ) -> list[Any]:
        results = []
        for quadrant in unlocked_quadrants:
            cost = self._get_land_cost(quadrant)
            if cost > available_cash:
                continue
            result = self._evaluate_quadrant(
                quadrant=quadrant,
                cost=cost,
                remaining_turns=remaining_turns,
                farm_profit_per_turn=farm_profit_per_turn,
            )
            if result:
                results.append(result)
        return results

    def _get_land_cost(self, quadrant: str) -> float:
        costs = {"NE": 1000, "SW": 2000, "SE": 4000}
        return costs.get(quadrant, 0)

    def _evaluate_quadrant(
        self,
        quadrant: str,
        cost: float,
        remaining_turns: int,
        farm_profit_per_turn: float,
    ) -> Any:
        return None

    def set_land_data(self, land_type: str, data: dict) -> None:
        self._land_data[land_type] = data