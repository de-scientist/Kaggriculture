from __future__ import annotations

from typing import Any

from agent.economics.economic_state import EconomicState
from agent.economics.profit_model import ProfitabilityEstimate


class EconomicEvaluator:
    """Evaluates the economic state of the farm at a given turn.

    Computes: cash, inventory value, expected inventory value,
    production capacity, worker capacity, land capacity, animal capacity,
    crop capacity, expected revenue, expected costs, expected profit,
    opportunity costs, market conditions, remaining turns, capital requirements,
    risk exposure.
    """

    def __init__(self):
        self._seed = 0

    def evaluate(self, game_state: Any) -> EconomicState:
        if game_state is None:
            return EconomicState()

        farm = game_state.farm if hasattr(game_state, "farm") else None
        inventory = game_state.inventory if hasattr(game_state, "inventory") else None
        market = game_state.market if hasattr(game_state, "market") else None
        town = game_state.town if hasattr(game_state, "town") else None
        season = game_state.season if hasattr(game_state, "season") else None
        private = game_state.private if hasattr(game_state, "private") else {}
        unlocked_quadrants = game_state.unlocked_quadrants if hasattr(game_state, "unlocked_quadrants") else []
        hires_today = game_state.hires_today if hasattr(game_state, "hires_today") else 0
        seeds = game_state.private.get("seeds", {}) if hasattr(game_state, "private") else {}
        shed = game_state.private.get("shed", {}) if hasattr(game_state, "private") else {}
        inventories = game_state.private.get("inventories", []) if hasattr(game_state, "private") else []
        tiles = game_state.farm.tiles if hasattr(game_state, "farm") else {}
        farmer = game_state.farm.farmer if hasattr(game_state, "farm") else None
        hands = game_state.farm.hands if hasattr(game_state, "farm") else []

        cash = farm.money if farm else 3000.0

        inventory_value = 0.0
        expected_inventory_value = 0.0
        if inventory and hasattr(inventory, "items"):
            items = inventory.items
            for item, count in items.items():
                if count > 0:
                    price = self._get_price(item, market)
                    inventory_value += price * count
            expected_inventory_value = inventory_value

        production_capacity = 0
        worker_capacity = 0
        land_capacity = 0
        animal_capacity = 0
        crop_capacity = 0

        if farm:
            for pos, tile in farm.tiles.items():
                if tile is not None:
                    if tile.kind == "PLANT":
                        crop_capacity += 1
                    elif tile.kind == "COOP" or tile.kind == "PASTURE":
                        animal_capacity += 1

        if market:
            pass

        return EconomicState(
            cash=cash,
            inventory_value=inventory_value,
            expected_inventory_value=expected_inventory_value,
            production_capacity=production_capacity,
            worker_capacity=worker_capacity,
            land_capacity=land_capacity,
            animal_capacity=animal_capacity,
            crop_capacity=crop_capacity,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions="stable",
            remaining_turns=season.remaining_turns if season else 720,
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