from __future__ import annotations

from dataclasses import dataclass

from agent.economics.profit_model import CROP_PARAMS


@dataclass
class CropRecommendation:
    crop_type: str
    score: float
    expected_profit: float = 0.0
    expected_cost: float = 0.0
    time_to_harvest: int = 0


class CropOptimizer:
    """Optimizes crop portfolio selection.

    Evaluates each crop against:
    * capital constraints (seed cost)
    * remaining season length
    * market prices
    * seed availability
    """

    TURNS_PER_DAY = 24

    def __init__(self):
        self._crop_data: dict[str, dict] = {}
        self._portfolio: list[CropRecommendation] = []
        for crop_type, params in CROP_PARAMS.items():
            self._crop_data[crop_type] = {
                "seed_cost": float(params["price"]),
                "first_yield_day": int(params["first_yield_day"]),
                "max_yield_day": int(params["max_yield_day"]),
                "sell_price": float(params["sell_price"]),
                "ongoing": bool(params.get("ongoing", False)),
            }

    def evaluate_planting(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        planted_tiles: dict | None = None,
    ) -> list[CropRecommendation]:
        planted_tiles = planted_tiles or {}
        results: list[CropRecommendation] = []
        for crop_type, data in self._crop_data.items():
            if available_seeds.get(crop_type, 0) <= 0:
                continue
            seed_cost = data["seed_cost"]
            if seed_cost > available_cash:
                continue
            first_yield = data["first_yield_day"]
            if remaining_turns < first_yield * self.TURNS_PER_DAY:
                continue
            sale_price = market_prices.get(crop_type, data["sell_price"])
            expected_yield = 1 + max(0, data["max_yield_day"] - first_yield)
            expected_revenue = sale_price * expected_yield
            expected_profit = expected_revenue - seed_cost
            time_to_harvest = first_yield * self.TURNS_PER_DAY
            score = expected_profit / max(time_to_harvest, 1)
            results.append(
                CropRecommendation(
                    crop_type=crop_type,
                    score=score,
                    expected_profit=expected_profit,
                    expected_cost=seed_cost,
                    time_to_harvest=time_to_harvest,
                )
            )
        results.sort(key=lambda r: (-r.score, r.crop_type))
        return results

    def optimal_crop(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        planted_tiles: dict,
    ) -> CropRecommendation | None:
        recs = self.evaluate_planting(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_seeds=available_seeds,
            available_cash=available_cash,
            planted_tiles=planted_tiles,
        )
        return recs[0] if recs else None

    def portfolio(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_seeds: dict[str, int],
        available_cash: float,
        max_plantings: int = 3,
    ) -> list[CropRecommendation]:
        recs = self.evaluate_planting(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_seeds=available_seeds,
            available_cash=available_cash,
            planted_tiles={},
        )
        portfolio = recs[:max_plantings]
        self._portfolio = portfolio
        return portfolio

    def set_crop_data(self, crop_type: str, data: dict) -> None:
        self._crop_data[crop_type] = data

    def get_portfolio(self) -> list[CropRecommendation]:
        return self._portfolio
