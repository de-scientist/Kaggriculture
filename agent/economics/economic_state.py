from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.domain.farm import Farm
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.season import Season
from agent.economics.profit_model import CROP_PARAMS


@dataclass
class CashRecord:
    cash: float
    liquid_inventory_value: float
    useful_asset_value: float
    known_obligations: float
    current_wealth: float
    expected_wealth: float
    potential_wealth: float


def _reserved_amount(capital_requirements: float | dict) -> float:
    """Extract the reserved portion of capital requirements."""
    if isinstance(capital_requirements, dict):
        return float(capital_requirements.get("reserved", 0.0))
    return float(capital_requirements or 0.0)


@dataclass
class EconomicState:
    """Economic representation of the farm at the current turn.

    Derived from the canonical GameState rather than maintaining a second
    source of truth. All values reflect the current turn only; nothing here
    is computed from future information.
    """

    cash: float
    shed_inventory_value: float
    seed_inventory_value: float
    production_capacity: float
    worker_count: int
    worker_capacity: int
    land_tiles: int
    land_capacity: int
    animal_count: int
    animal_capacity: int
    expected_revenue: float
    expected_costs: float
    expected_profit: float
    opportunity_costs: dict[str, float]
    market_conditions: dict | str
    remaining_turns: int
    capital_requirements: float | dict
    risk_exposure: float
    net_worth: float
    expected_net_worth: float
    potential_net_worth: float
    current_game_state: Any = None
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
    farmer: Any | None = field(default=None)
    hands: list[list] = field(default_factory=list)
    inventory_value: float = 0.0
    expected_inventory_value: float = 0.0

    @property
    def available_capital(self) -> float:
        return max(0.0, self.cash - _reserved_amount(self.capital_requirements))

    @property
    def profit_per_turn(self) -> float:
        if self.remaining_turns <= 0:
            return 0.0
        return self.expected_profit / self.remaining_turns

    def liquid_narrative(self) -> str:
        return (
            f"Cash: {self.cash:.1f} | "
            f"Inventory Value: {self.inventory_value:.1f} | "
            f"Net Worth: {self.net_worth:.1f} | "
            f"Remaining Turns: {self.remaining_turns}"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cash": self.cash,
            "shed_inventory_value": self.shed_inventory_value,
            "seed_inventory_value": self.seed_inventory_value,
            "inventory_value": self.inventory_value,
            "expected_inventory_value": self.expected_inventory_value,
            "production_capacity": self.production_capacity,
            "worker_count": self.worker_count,
            "worker_capacity": self.worker_capacity,
            "land_tiles": self.land_tiles,
            "land_capacity": self.land_capacity,
            "animal_count": self.animal_count,
            "animal_capacity": self.animal_capacity,
            "expected_revenue": self.expected_revenue,
            "expected_costs": self.expected_costs,
            "expected_profit": self.expected_profit,
            "opportunity_costs": self.opportunity_costs,
            "market_conditions": self.market_conditions,
            "remaining_turns": self.remaining_turns,
            "capital_requirements": self.capital_requirements,
            "risk_exposure": self.risk_exposure,
            "net_worth": self.net_worth,
            "expected_net_worth": self.expected_net_worth,
            "potential_net_worth": self.potential_net_worth,
        }


class EconomicEvaluator:
    """Evaluates the economic state of the farm at a given turn.

    Computes: cash, inventory value, shed value, seed value, capacities,
    expected revenue/costs/profit, opportunity costs, market conditions,
    remaining turns, capital requirements, and risk exposure — all from the
    current GameState only.
    """

    def __init__(self):
        self._seed: int = 0

    def evaluate(self, game_state: Any) -> EconomicState:
        if game_state is None:
            return EconomicState(
                cash=3000.0,
                shed_inventory_value=0.0,
                seed_inventory_value=0.0,
                production_capacity=0.0,
                worker_count=0,
                worker_capacity=0,
                land_tiles=0,
                land_capacity=0,
                animal_count=0,
                animal_capacity=0,
                expected_revenue=0.0,
                expected_costs=0.0,
                expected_profit=0.0,
                opportunity_costs={},
                market_conditions="stable",
                remaining_turns=720,
                capital_requirements=0.0,
                risk_exposure=0.0,
                net_worth=3000.0,
                expected_net_worth=3000.0,
                potential_net_worth=3000.0,
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
        prices = market.prices if (market and hasattr(market, "prices")) else {}

        inventory_value = 0.0
        if inventory and hasattr(inventory, "items"):
            for item, count in inventory.items.items():
                if count > 0:
                    inventory_value += prices.get(item, 1) * count

        shed_inventory_value = 0.0
        for item, count in shed.items():
            if count > 0:
                shed_inventory_value += prices.get(item, 1) * count

        seed_inventory_value = 0.0
        for crop, count in seeds.items():
            if count > 0:
                params = CROP_PARAMS.get(crop)
                seed_value = float(params["price"]) if params else 1.0
                seed_inventory_value += seed_value * count

        workers = farm.workers if (farm and hasattr(farm, "workers")) else []
        worker_count = len(workers)
        worker_capacity = worker_count if worker_count > 0 else 1

        crop_capacity = 0
        animal_capacity = 0
        animal_count = 0
        for tile in tiles.values():
            if tile is not None:
                if isinstance(tile, dict):
                    if tile.get("kind") == "PLANT":
                        crop_capacity += 1
                    elif tile.get("kind") in ("COOP", "PASTURE"):
                        animal_capacity += 1
                        if tile.get("animal") is not None:
                            animal_count += 1

        unlocked = [q for q in unlocked_quadrants if q != "LOCKED"]
        land_tiles = len(tiles) if tiles else len(unlocked) * 25
        production_capacity = float(crop_capacity + animal_capacity)
        land_capacity = land_tiles

        if season and hasattr(season, "remaining_turns"):
            remaining_turns = season.remaining_turns
        else:
            remaining_turns = 720

        net_worth = cash + inventory_value + shed_inventory_value + seed_inventory_value
        expected_net_worth = net_worth
        potential_net_worth = net_worth

        return EconomicState(
            cash=cash,
            shed_inventory_value=shed_inventory_value,
            seed_inventory_value=seed_inventory_value,
            production_capacity=production_capacity,
            worker_count=worker_count,
            worker_capacity=worker_capacity,
            land_tiles=land_tiles,
            land_capacity=land_capacity,
            animal_count=animal_count,
            animal_capacity=animal_capacity,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions="stable",
            remaining_turns=remaining_turns,
            capital_requirements=0.0,
            risk_exposure=0.0,
            net_worth=net_worth,
            expected_net_worth=expected_net_worth,
            potential_net_worth=potential_net_worth,
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
            inventory_value=inventory_value,
            expected_inventory_value=inventory_value + shed_inventory_value,
        )

    def set_seed(self, seed: int) -> None:
        self._seed = seed
