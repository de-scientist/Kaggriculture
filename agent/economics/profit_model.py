from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.economics.economic_state import EconomicState
from agent.economics.profit_model import ProfitabilityEstimate


@dataclass
class ProfitabilityEstimate:
    crop: str
    seed_cost: float
    water_cost: float
    fertilizer_cost: float
    growth_days: int
    worker_requirement: int
    expected_yield: int
    expected_sale_price: float
    expected_revenue: float
    expected_net_profit: float
    profit_per_turn: float
    capital_efficiency: float
    land_efficiency: float


class ProfitabilityEngine:
    """Estimates profitability of crop, animal, and land investments.

    Calculates:
    * Gross revenue
    * Net revenue
    * Time to completion
    * Resource requirements
    * Labor requirements
    * Expected return
    * Return per turn
    * Return on capital
    """

    def __init__(self):
        self._crop_data = {}
        self._animal_data = {}
        self._land_data = {}

    def estimate_crop_profitability(
        self,
        crop_type: str,
        seed_cost: float,
        water_requirement: int,
        fertilizer_requirement: int,
        growth_days: int,
        worker_requirement: int,
        expected_yield: int,
        expected_sale_price: float,
    ) -> ProfitabilityEstimate:
        net_profit = expected_sale_price * expected_yield - seed_cost - water_requirement * 0.1 - fertilizer_requirement * 0.1
        profit_per_turn = net_profit / growth_days
        capital_efficiency = expected_sale_price * expected_yield / max(seed_cost, 0.01)
        land_efficiency = expected_yield / max(growth_days, 1)
        return ProfitabilityEstimate(
            crop=crop_type,
            seed_cost=seed_cost,
            water_cost=water_requirement,
            fertilizer_cost=fertilizer_requirement,
            growth_days=growth_days,
            worker_requirement=worker_requirement,
            expected_yield=expected_yield,
            expected_sale_price=expected_sale_price,
            expected_revenue=expected_sale_price * expected_yield,
            expected_net_profit=net_profit,
            profit_per_turn=profit_per_turn,
            capital_efficiency=capital_efficiency,
            land_efficiency=land_efficiency,
        )

    def estimate_animal_profitability(
        self,
        animal_type: str,
        purchase_cost: float,
        feed_cost: float,
        production_rate: int,
        product_value: float,
        worker_requirement: int,
        feed_days: int,
    ) -> ProfitabilityEstimate:
        payback_turns = purchase_cost / max(product_value, 0.01)
        net_profit = product_value * production_rate - feed_cost * feed_days - purchase_cost
        profit_per_turn = net_profit / feed_days if feed_days > 0 else 0.0
        capital_efficiency = product_value * production_rate / max(purchase_cost, 0.01)
        land_efficiency = production_rate / max(feed_days, 1)
        return ProfitabilityEstimate(
            crop=animal_type,
            seed_cost=purchase_cost,
            water_cost=0,
            fertilizer_cost=0,
            growth_days=feed_days,
            worker_requirement=worker_requirement,
            expected_yield=production_rate,
            expected_sale_price=product_value,
            expected_revenue=product_value * production_rate,
            expected_net_profit=net_profit,
            profit_per_turn=profit_per_turn,
            capital_efficiency=capital_efficiency,
            land_efficiency=land_efficiency,
        )

    def estimate_land_profitability(
        self,
        cost: float,
        additional_capacity: int,
        expected_revenue_per_turn: float,
        remaining_turns: int,
    ) -> ProfitabilityEstimate:
        total_return = expected_revenue_per_turn * remaining_turns
        net_return = total_return - cost
        profit_per_turn = expected_revenue_per_turn
        capital_efficiency = net_return / max(cost, 0.01)
        land_efficiency = expected_revenue_per_turn
        return ProfitabilityEstimate(
            crop="LAND",
            seed_cost=0,
            water_cost=0,
            fertilizer_cost=0,
            growth_days=remaining_turns,
            worker_requirement=0,
            expected_yield=additional_capacity,
            expected_sale_price=expected_revenue_per_turn,
            expected_revenue=total_return,
            expected_net_profit=net_return,
            profit_per_turn=profit_per_turn,
            capital_efficiency=capital_efficiency,
            land_efficiency=land_efficiency,
        )