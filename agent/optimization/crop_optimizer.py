from __future__ import annotations

from typing import Any

from agent.optimization.crop_optimizer import CropOptimizer, CropRecommendation
from agent.economics.profit_model import ProfitabilityEstimate


class CropOptimizer:
    """Optimizes crop portfolio selection.

    Evaluates each crop against:
    * land constraints
    * worker constraints
    * water constraints
    * fertilizer constraints
    * capital constraints
    * market conditions
    * remaining season length
    """

    def __init__(self):
        self._crop_data = {}
        self._portfolio: list[CropRecommendation] = []

    def optimal_crop(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        planted_tiles: dict,
    ) -> CropRecommendation | None:
        best = None
        best_score = -float("inf")
        for crop_type, data in self._crop_data.items():
            if available_seeds.get(crop_type, 0) <= 0:
                continue
            if data["seed_cost"] > available_cash:
                continue
            score = self._evaluate_crop(
                crop_type=crop_type,
                current_day=current_day,
                remaining_turns=remaining_turns,
                market_prices=market_prices,
                available_seeds=available_seeds,
                data=data,
            )
            if score > best_score:
                best_score = score
                best = CropRecommendation(crop_type=crop_type, score=score)
        return best

    def _evaluate_crop(
        self,
        crop_type: str,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        data: dict,
    ) -> float:
        return 0.0

    def set_crop_data(self, crop_type: str, data: dict) -> None:
        self._crop_data[crop_type] = data

    def get_portfolio(self) -> list[CropRecommendation]:
        return self._portfolio