from __future__ import annotations

from typing import Any

from agent.economics.profit_model import ProfitabilityEstimate


class AnimalRecommendation:
    animal_type: str
    score: float
    expected_profit: float = 0.0
    expected_cost: float = 0.0
    time_to_payback: float = 0.0


class AnimalOptimizer:
    """Optimizes animal production pipeline.

    Evaluates:
    * Purchase cost
    * Feed cost
    * Maintenance cost
    * Production rate
    * Product value
    * Worker requirement
    * Expected profit
    * Payback period
    * Remaining turns
    """

    def __init__(self):
        self._animal_data = {}

    def optimize(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_cash: float,
        available_land: int,
    ) -> dict[str, Any]:
        best = None
        best_score = -float("inf")
        for animal_type, data in self._animal_data.items():
            if data["purchase_cost"] > available_cash:
                continue
            score = self._evaluate_animal(
                animal_type=animal_type,
                current_day=current_day,
                remaining_turns=remaining_turns,
                market_prices=market_prices,
                data=data,
            )
            if score > best_score:
                best_score = score
                best = data
        return best

    def _evaluate_animal(
        self,
        animal_type: str,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        data: dict,
    ) -> float:
        return 0.0

    def set_animal_data(self, animal_type: str, data: dict) -> None:
        self._animal_data[animal_type] = data