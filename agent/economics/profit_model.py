"""Stage 2 — Profitability estimation for crops and animals.

Estimates expected revenue, cost, profit, completion window, and ROI for a
crop or animal investment from the current turn. All estimates are based on
the static crop/animal parameter tables and the current day only — never on
future market or game data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TURNS_PER_DAY = 24


@dataclass
class ProfitabilityEstimate:
    """Profitability estimate for a crop, animal, or land investment."""

    name: str
    seed_cost: float
    expected_revenue: float
    expected_yield: int
    expected_sale_price: float
    growth_duration: int
    remaining_season: int
    feed_cost: float = 0.0

    @property
    def total_cost(self) -> float:
        return self.seed_cost + self.feed_cost

    @property
    def expected_profit(self) -> float:
        return self.expected_revenue - self.total_cost

    @property
    def can_complete(self) -> bool:
        return 0 <= self.growth_duration <= self.remaining_season

    @property
    def roi(self) -> float:
        if self.seed_cost <= 0:
            return 0.0
        return (self.expected_revenue - self.seed_cost) / self.seed_cost * 100.0


# Crop parameters (seed cost is ``price``; base sale price is ``sell_price``)
CROP_PARAMS: dict[str, dict[str, Any]] = {
    "WHEAT": {
        "price": 10,
        "first_yield_day": 2,
        "max_yield_day": 4,
        "sell_price": 25,
        "ongoing": False,
    },
    "CARROT": {
        "price": 20,
        "first_yield_day": 3,
        "max_yield_day": 6,
        "sell_price": 35,
        "ongoing": False,
    },
    "TOMATO": {
        "price": 30,
        "first_yield_day": 8,
        "max_yield_day": 9,
        "sell_price": 60,
        "ongoing": True,
    },
    "STRAWBERRY": {
        "price": 40,
        "first_yield_day": 10,
        "max_yield_day": 12,
        "sell_price": 120,
        "ongoing": True,
    },
    "MELON": {
        "price": 50,
        "first_yield_day": 5,
        "max_yield_day": 10,
        "sell_price": 250,
        "ongoing": False,
    },
}

# Animal parameters (purchase cost is ``price``; product base price is
# ``product_base_price``)
ANIMAL_PARAMS: dict[str, dict[str, Any]] = {
    "GOOSE": {
        "price": 30,
        "product": "EGG",
        "product_base_price": 40,
        "production_interval": 4,
        "feed": "WHEAT",
        "feed_quantity": 1,
        "first_yield_day": 4,
    },
    "COW": {
        "price": 50,
        "product": "MILK",
        "product_base_price": 80,
        "production_interval": 3,
        "feed": "WHEAT",
        "feed_quantity": 1,
        "first_yield_day": 8,
    },
    "SHEEP": {
        "price": 70,
        "product": "WOOL",
        "product_base_price": 100,
        "production_interval": 4,
        "feed": "WHEAT",
        "feed_quantity": 1,
        "first_yield_day": 6,
    },
}


def estimate_crop_profitability(
    crop_type: str,
    current_day: int = 0,
    remaining_turns: int = 720,
) -> ProfitabilityEstimate:
    """Estimate profitability of planting ``crop_type`` at ``current_day``.

    Unknown crops default to WHEAT parameters. ``growth_duration`` is the
    number of days until the crop's ``max_yield_day``; a negative value means
    the crop cannot reach maturity within the season.
    """
    params = CROP_PARAMS.get(crop_type) or CROP_PARAMS["WHEAT"]
    seed_cost = float(params["price"])
    first_yield_day = int(params["first_yield_day"])
    max_yield_day = int(params["max_yield_day"])
    sell_price = float(params["sell_price"])
    expected_yield = 1 + max(0, max_yield_day - first_yield_day)
    expected_revenue = sell_price * expected_yield
    growth_duration = max_yield_day - current_day
    return ProfitabilityEstimate(
        name=f"crop_{crop_type}",
        seed_cost=seed_cost,
        expected_revenue=expected_revenue,
        expected_yield=expected_yield,
        expected_sale_price=sell_price,
        growth_duration=growth_duration,
        remaining_season=remaining_turns,
    )


def estimate_animal_profitability(
    animal_type: str,
    current_day: int = 0,
    remaining_turns: int = 720,
) -> ProfitabilityEstimate:
    """Estimate profitability of buying and raising ``animal_type``.

    Unknown animals default to GOOSE parameters. Expected revenue and feed
    cost are projected over the number of production cycles that fit in the
    remaining season.
    """
    params = ANIMAL_PARAMS.get(animal_type) or ANIMAL_PARAMS["GOOSE"]
    purchase_cost = float(params["price"])
    product_base_price = float(params["product_base_price"])
    production_interval = max(1, int(params["production_interval"]))
    feed_quantity = max(1, int(params["feed_quantity"]))
    first_yield_day = int(params.get("first_yield_day", 4))
    wheat_price = float(CROP_PARAMS["WHEAT"]["price"])

    cycles = max(1, remaining_turns // (production_interval * TURNS_PER_DAY))
    feed_cost = wheat_price * feed_quantity * cycles
    expected_revenue = product_base_price * cycles
    growth_duration = first_yield_day - current_day
    return ProfitabilityEstimate(
        name=f"animal_{animal_type}",
        seed_cost=purchase_cost,
        expected_revenue=expected_revenue,
        expected_yield=cycles,
        expected_sale_price=product_base_price,
        growth_duration=growth_duration,
        remaining_season=remaining_turns,
        feed_cost=feed_cost,
    )


class ProfitabilityEngine:
    """Convenience facade around the profitability estimation functions."""

    def estimate_crop_profitability(
        self,
        crop_type: str,
        current_day: int = 0,
        remaining_turns: int = 720,
    ) -> ProfitabilityEstimate:
        return estimate_crop_profitability(
            crop_type,
            current_day=current_day,
            remaining_turns=remaining_turns,
        )

    def estimate_animal_profitability(
        self,
        animal_type: str,
        current_day: int = 0,
        remaining_turns: int = 720,
    ) -> ProfitabilityEstimate:
        return estimate_animal_profitability(
            animal_type,
            current_day=current_day,
            remaining_turns=remaining_turns,
        )
