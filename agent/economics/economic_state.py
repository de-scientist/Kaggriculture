from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.domain.farm import Farm
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.player import Player
from agent.domain.season import Season
from agent.domain.wallet import Wallet


@dataclass
class CashRecord:
    cash: float
    liquid_inventory_value: float
    useful_asset_value: float
    known_obligations: float
    current_wealth: float
    expected_wealth: float
    potential_wealth: float


@dataclass
class EconomicState:
    cash: float
    inventory_value: float
    expected_inventory_value: float
    production_capacity: int
    worker_capacity: int
    land_capacity: int
    animal_capacity: int
    crop_capacity: int
    expected_revenue: float
    expected_costs: float
    expected_profit: float
    opportunity_costs: dict[str, float]
    market_conditions: str
    remaining_turns: int
    capital_requirements: float
    risk_exposure: float
    current_game_state: Any
    farm: Farm | None = field(default=None)
    inventory: Inventory | None = field(default=None)
    market: Market | None = field(default=None)
    town: Any | None = field(default=None)
    season: Season | None = field(default=None)
    private: dict = field(default_factory=dict)
    unlocked_quadrants: list[str] = field(default_factory=list)
    hires_today: int = field(default=0)
    seeds: dict[str, int] = field(default_factory=dict)
    shed: dict[str, int] = field(default_factory=dict)
    inventories: list[dict] = field(default_factory=list)
    crops: list[dict] = field(default_factory=list)
    animals: list[dict] = field(default_factory=list)
    tiles: dict = field(default_factory=dict)
    farmer: tuple[int, int] | None = field(default=None)
    hands: list[list] = field(default_factory=list)
    unlocked_quadrants_list: list[str] = field(default_factory=list)

    def liquid_narrative(self) -> str:
        return (
            f"Cash: {self.cash:.1f} | "
            f"Inventory Value: {self.inventory_value:.1f} | "
            f"Expected Wealth: {self.expected_wealth:.1f} | "
            f"Remaining Turns: {self.remaining_turns}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cash": self.cash,
            "inventory_value": self.inventory_value,
            "expected_inventory_value": self.expected_inventory_value,
            "production_capacity": self.production_capacity,
            "worker_capacity": self.worker_capacity,
            "land_capacity": self.land_capacity,
            "animal_capacity": self.animal_capacity,
            "crop_capacity": self.crop_capacity,
            "expected_revenue": self.expected_revenue,
            "expected_costs": self.expected_costs,
            "expected_profit": self.expected_profit,
            "opportunity_costs": self.opportunity_costs,
            "market_conditions": self.market_conditions,
            "remaining_turns": self.remaining_turns,
            "capital_requirements": self.capital_requirements,
            "risk_exposure": self.risk_exposure,
            "current_game_state": self.current_game_state,
        }