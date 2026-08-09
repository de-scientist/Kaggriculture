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
    """Economic representation of the farm state.

    Derived from the canonical GameState rather than maintaining
    a second source of truth.
    """

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
    hires_today: int = 0
    seeds: dict[str, int] = field(default_factory=dict)
    shed: dict[str, int] = field(default_factory=dict)
    inventories: list[dict] = field(default_factory=list)
    crops: list[dict] = field(default_factory=list)
    animals: list[dict] = field(default_factory=list)
    tiles: dict = field(default_factory=dict)
    farmer: tuple[int, int] | None = field(default=None)
    hands: list[list] = field(default_factory=list)

    @property
    def available_capital(self) -> float:
        return max(0.0, self.cash - self.capital_requirements)

    def liquid_narrative(self) -> str:
        return (
            f"Cash: {self.cash:.1f} | "
            f"Inventory Value: {self.inventory_value:.1f} | "
            f"Expected Wealth: {self.cash + self.expected_inventory_value:.1f} | "
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


class EconomicEvaluator:
    """Evaluates the economic state of the farm at a given turn.

    Computes: cash, inventory value, expected inventory value,
    production capacity, worker capacity, land capacity, animal capacity,
    crop capacity, expected revenue, expected costs, expected profit,
    opportunity costs, market conditions, remaining turns, capital requirements,
    risk exposure.
    """

    def __init__(self):
        self._seed: int = 0

    def evaluate(self, game_state: Any) -> EconomicState:
        if game_state is None:
            return EconomicState(
                cash=3000.0,
                inventory_value=0.0,
                expected_inventory_value=0.0,
                production_capacity=0,
                worker_capacity=0,
                land_capacity=0,
                animal_capacity=0,
                crop_capacity=0,
                expected_revenue=0.0,
                expected_costs=0.0,
                expected_profit=0.0,
                opportunity_costs={},
                market_conditions="stable",
                remaining_turns=720,
                capital_requirements=0.0,
                risk_exposure=0.0,
                current_game_state=None,
            )

        farm = getattr(game_state, "farm", None)
        inventory = getattr(game_state, "inventory", None)
        market = getattr(game_state, "market", None)
        town = getattr(game_state, "town", None)
        season = getattr(game_state, "season", None)
        private = getattr(game_state, "private", {})
        unlocked_quadrants = getattr(game_state, "unlocked_quadrants", [])
        hires_today = getattr(game_state, "hires_today", 0)
        seeds = private.get("seeds", {})
        shed = private.get("shed", {})
        inventories = private.get("inventories", [])
        tiles = farm.tiles if farm and hasattr(farm, "tiles") else {}
        farmer = farm.farmer if farm and hasattr(farm, "farmer") else None
        hands = farm.hands if farm and hasattr(farm, "hands") else []

        cash = farm.money if farm and hasattr(farm, "money") else 3000.0

        inventory_value = 0.0
        if inventory and hasattr(inventory, "items"):
            items = inventory.items
            prices = market.prices if (market and hasattr(market, "prices")) else {}
            for item, count in items.items():
                if count > 0:
                    price = prices.get(item, 1)
                    inventory_value += price * count

        production_capacity = 0
        worker_capacity = 0
        land_capacity = 0
        animal_capacity = 0
        crop_capacity = 0

        if farm:
            worker_capacity = len(farm.workers) if hasattr(farm, "workers") else 1
            for pos, tile in (farm.tiles if hasattr(farm, "tiles") else {}).items():
                if tile is not None:
                    if isinstance(tile, dict):
                        if tile.get("kind") == "PLANT":
                            crop_capacity += 1
                        elif tile.get("kind") in ("COOP", "PASTURE"):
                            animal_capacity += 1

        remaining_turns = season.remaining_turns if (season and hasattr(season, "remaining_turns")) else 720

        return EconomicState(
            cash=cash,
            inventory_value=inventory_value,
            expected_inventory_value=inventory_value,
            production_capacity=production_capacity,
            worker_capacity=worker_capacity,
            land_capacity=len([q for q in unlocked_quadrants if q != "LOCKED"]) * 25,
            animal_capacity=animal_capacity,
            crop_capacity=crop_capacity,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions="stable",
            remaining_turns=remaining_turns,
            capital_requirements=0.0,
            risk_exposure=0.0,
            current_game_state=game_state,
            farm=farm,
            inventory=inventory,
            market=market,
            town=town,
            season=season,
            private=private,
            unlocked_quadrants=unlocked_quadrants,
            hires_today=hires_today,
            seeds=seeds,
            shed=shed,
            inventories=inventories,
            tiles=tiles,
            farmer=farmer,
            hands=hands,
        )

    def set_seed(self, seed: int) -> None:
        self._seed = seed
