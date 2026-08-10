from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
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
    * Required structure (coop / pasture)
    * Feed cost
    * Production rate
    * Product value
    * Expected profit
    * Payback period
    """

    TURNS_PER_DAY = 24

    def __init__(self) -> None:
        self._animal_data: dict[str, dict[str, Any]] = {
            "GOOSE": {
                "purchase_cost": 100.0,
                "structure": "COOP",
                "product": "EGG",
                "production_interval": 4,
                "feed": "WHEAT",
                "feed_quantity": 1,
                "base_price": 40.0,
            },
            "COW": {
                "purchase_cost": 200.0,
                "structure": "PASTURE",
                "product": "MILK",
                "production_interval": 3,
                "feed": "WHEAT",
                "feed_quantity": 1,
                "base_price": 80.0,
            },
            "SHEEP": {
                "purchase_cost": 300.0,
                "structure": "PASTURE",
                "product": "WOOL",
                "production_interval": 4,
                "feed": "WHEAT",
                "feed_quantity": 1,
                "base_price": 100.0,
            },
        }

    def evaluate_purchase(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_cash: float,
        existing_animals: dict[str, int],
        has_structure: dict[str, bool],
    ) -> list[AnimalRecommendation]:
        if available_cash <= 0:
            return []
        results: list[AnimalRecommendation] = []
        remaining_days = max(1, remaining_turns // self.TURNS_PER_DAY)
        for animal_type, data in self._animal_data.items():
            cost = float(data["purchase_cost"])
            if cost > available_cash:
                continue
            required = str(data["structure"])
            if not has_structure.get(required):
                continue
            product = str(data["product"])
            price = market_prices.get(product, float(data["base_price"]))
            interval = int(data["production_interval"])
            productions = max(0.0, remaining_days / interval)
            expected_revenue = price * productions
            feed = str(data["feed"])
            feed_cost = float(data["feed_quantity"]) * remaining_days * market_prices.get(feed, 0)
            expected_cost = cost + feed_cost
            expected_profit = expected_revenue - expected_cost
            score = expected_profit / max(remaining_turns, 1)
            payback = cost / max(price, 0.01) if price > 0 else float("inf")
            results.append(
                AnimalRecommendation(
                    animal_type=animal_type,
                    score=score,
                    expected_profit=expected_profit,
                    expected_cost=expected_cost,
                    time_to_payback=payback,
                )
            )
        results.sort(key=lambda r: (-r.score, r.animal_type))
        return results

    def best_purchase(
        self,
        current_day: int,
        remaining_turns: int,
        market_prices: dict[str, int],
        available_cash: float,
        existing_animals: dict[str, int],
        has_structure: dict[str, bool],
    ) -> AnimalRecommendation | None:
        recs = self.evaluate_purchase(
            current_day=current_day,
            remaining_turns=remaining_turns,
            market_prices=market_prices,
            available_cash=available_cash,
            existing_animals=existing_animals,
            has_structure=has_structure,
        )
        return recs[0] if recs else None

    def set_animal_data(self, animal_type: str, data: dict) -> None:
        self._animal_data[animal_type] = data
