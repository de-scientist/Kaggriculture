from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EconomicEvaluation:
    net_worth: float = 0.0
    expected_wealth: float = 0.0
    potential_wealth: float = 0.0
    cash: float = 0.0
    expected_revenue: float = 0.0
    expected_costs: float = 0.0
    expected_profit: float = 0.0
    opportunity_costs: dict[str, float] = field(default_factory=dict)
    market_conditions: str = "unknown"
    remaining_turns: int = 0
    capital_requirements: float = 0.0
    risk_exposure: float = 0.0
    crop_portfolio: list[dict[str, Any]] = field(default_factory=list)
    animal_portfolio: list[dict[str, Any]] = field(default_factory=list)
    land_investment: list[dict[str, Any]] = field(default_factory=list)
    worker_allocation: dict[str, int] = field(default_factory=dict)


class EconomicEvaluator:
    """Evaluates the economic state of the farm at a given turn."""

    def __init__(self) -> None:
        self._crop_optimizer = None
        self._animal_optimizer = None
        self._worker_optimizer = None
        self._land_optimizer = None

    def evaluate(
        self,
        game_state: Any,
    ) -> EconomicEvaluation:
        if game_state is None:
            return EconomicEvaluation()

        farm = game_state.farm if hasattr(game_state, "farm") else None
        inventory = game_state.inventory if hasattr(game_state, "inventory") else None
        market = game_state.market if hasattr(game_state, "market") else None
        season = game_state.season if hasattr(game_state, "season") else None

        cash = farm.money if farm else 3000.0

        inventory_value = 0.0
        if inventory and hasattr(inventory, "items"):
            items = inventory.items
            for item, count in items.items():
                if count > 0:
                    price = market.get_price(item) if market else 0
                    inventory_value += price * count

        return EconomicEvaluation(
            net_worth=cash,
            expected_wealth=0.0,
            potential_wealth=0.0,
            cash=cash,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions="stable",
            remaining_turns=season.remaining_turns if season else 720,
            capital_requirements=0.0,
            risk_exposure=0.0,
            crop_portfolio=[],
            animal_portfolio=[],
            land_investment=[],
            worker_allocation={},
        )
