"""Stage 2 — Profitability Engine.

Estimates the expected net profit of a production opportunity.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfitabilityEstimate:
    """Estimated profitability of a production opportunity."""

    name: str
    seed_cost: float
    water_cost: float = 0.0
    fertilizer_cost: float = 0.0
    feed_cost: float = 0.0
    worker_cost: float = 0.0
    expansion_cost: float = 0.0

    expected_yield: float = 0.0
    expected_sale_price: float = 0.0
    expected_revenue: float = 0.0

    growth_duration: int = 0
    remaining_season: int = 720

    @property
    def total_cost(self) -> float:
        return (
            self.seed_cost
            + self.water_cost
            + self.fertilizer_cost
            + self.feed_cost
            + self.worker_cost
            + self.expansion_cost
        )

    @property
    def expected_profit(self) -> float:
        return self.expected_revenue - self.total_cost

    @property
    def profit_per_turn(self) -> float:
        if self.growth_duration <= 0:
            return 0.0
        return self.expected_profit / self.growth_duration

    @property
    def roi(self) -> float:
        if self.total_cost <= 0:
            return 0.0
        return (self.expected_profit / self.total_cost) * 100.0

    @property
    def can_complete(self) -> bool:
        return self.growth_duration <= self.remaining_season

    @property
    def capital_efficiency(self) -> float:
        """Profit per unit of upfront capital."""
        if self.total_cost <= 0:
            return 0.0
        return self.expected_profit / self.total_cost

    @property
    def land_efficiency(self) -> float:
        """Profit per tile used."""
        if self.growth_duration <= 0:
            return 0.0
        return self.expected_profit / max(1, self.growth_duration)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "total_cost": self.total_cost,
            "expected_revenue": self.expected_revenue,
            "expected_profit": self.expected_profit,
            "roi": self.roi,
            "profit_per_turn": self.profit_per_turn,
            "can_complete": self.can_complete,
            "capital_efficiency": self.capital_efficiency,
            "growth_duration": self.growth_duration,
        }


# Crop profitability constants from official Kaggriculture rules
CROP_PARAMS: dict[str, dict] = {
    "WHEAT": {
        "seed_cost": 10,
        "first_yield_day": 2,
        "max_yield_day": 4,
        "base_yield": 1,
        "bonus_yield_per_water": 1,
        "base_price": 10,
    },
    "CARROT": {
        "seed_cost": 20,
        "first_yield_day": 3,
        "max_yield_day": 6,
        "base_yield": 2,
        "bonus_yield_per_water": 1,
        "base_price": 20,
    },
    "TOMATO": {
        "seed_cost": 30,
        "first_yield_day": 2,
        "max_yield_day": 8,
        "base_yield": 1,
        "ongoing": True,
        "base_price": 25,
    },
    "STRAWBERRY": {
        "seed_cost": 40,
        "first_yield_day": 1,
        "max_yield_day": 6,
        "base_yield": 1,
        "ongoing": True,
        "base_price": 50,
    },
    "MELON": {
        "seed_cost": 50,
        "first_yield_day": 5,
        "max_yield_day": 10,
        "base_yield": 3,
        "bonus_yield_per_water": 2,
        "base_price": 80,
    },
}

ANIMAL_PARAMS: dict[str, dict] = {
    "GOOSE": {
        "purchase_cost": 30,
        "feed_cost_per_day": 10,  # wheat cost
        "production_per_day": 1,
        "product": "EGG",
        "base_price": 30,
        "structure": "COOP",
    },
    "COW": {
        "purchase_cost": 50,
        "feed_cost_per_day": 10,
        "production_per_day": 1,
        "product": "MILK",
        "base_price": 50,
        "structure": "PASTURE",
    },
    "SHEEP": {
        "purchase_cost": 40,
        "feed_cost_per_day": 10,
        "production_per_day": 1,
        "product": "WOOL",
        "base_price": 40,
        "structure": "PASTURE",
    },
}


def estimate_crop_profitability(
    crop_type: str,
    current_day: int,
    remaining_turns: int,
    sale_price: int | None = None,
) -> ProfitabilityEstimate:
    """Estimate profitability of planting a crop at the current turn."""
    params = CROP_PARAMS.get(crop_type, CROP_PARAMS["WHEAT"])
    seed_cost = params["seed_cost"]
    max_yield_day = params["max_yield_day"]
    growth_duration = max_yield_day - current_day
    total_turns = min(growth_duration, remaining_turns)

    base_price = sale_price or params["base_price"]
    is_ongoing = params.get("ongoing", False)

    if is_ongoing:
        expected_revenue = base_price * params["base_yield"] * total_turns
    else:
        bonus_window_start = (max_yield_day + 1) // 2
        bonus_days = max(0, max_yield_day - bonus_window_start + 1)
        expected_yield = params["base_yield"] + bonus_days * params.get("bonus_yield_per_water", 1)
        expected_revenue = base_price * expected_yield

    return ProfitabilityEstimate(
        name=f"crop_{crop_type}",
        seed_cost=float(seed_cost),
        expected_yield=expected_yield if not is_ongoing else params["base_yield"] * total_turns,
        expected_sale_price=float(base_price),
        expected_revenue=float(expected_revenue),
        growth_duration=growth_duration if not is_ongoing else 1,
        remaining_season=remaining_turns,
    )


def estimate_animal_profitability(
    animal_type: str,
    current_day: int,
    remaining_turns: int,
    sale_price: int | None = None,
) -> ProfitabilityEstimate:
    """Estimate profitability of purchasing an animal at the current turn."""
    params = ANIMAL_PARAMS.get(animal_type, ANIMAL_PARAMS["GOOSE"])
    purchase_cost = params["purchase_cost"]
    feed_cost = params["feed_cost_per_day"] * remaining_turns
    base_price = sale_price or params["base_price"]
    expected_revenue = base_price * params["production_per_day"] * remaining_turns

    return ProfitabilityEstimate(
        name=f"animal_{animal_type}",
        seed_cost=float(purchase_cost),
        feed_cost=float(feed_cost),
        expected_sale_price=float(base_price),
        expected_revenue=float(expected_revenue),
        growth_duration=1,
        remaining_season=remaining_turns,
    )
