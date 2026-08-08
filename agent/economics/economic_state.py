"""Stage 2 — Economic State Model.

Derives an economic representation from the canonical GameState.
The economic model is computed fresh each turn; it never serves as a
second source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.domain.game_state import GameState


@dataclass(frozen=True)
class EconomicState:
    """Immutable snapshot of the farm's economic position."""

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
    market_conditions: dict[str, Any]
    remaining_turns: int
    capital_requirements: dict[str, float]
    risk_exposure: float
    net_worth: float
    expected_net_worth: float
    potential_net_worth: float

    @property
    def available_capital(self) -> float:
        return self.cash - self.capital_requirements.get("reserved", 0.0)

    @property
    def profit_per_turn(self) -> float:
        if self.remaining_turns <= 0:
            return 0.0
        return self.expected_profit / self.remaining_turns


@dataclass
class EconomicEvaluator:
    """Computes EconomicState from a GameState."""

    base_prices: dict[str, int] = field(
        default_factory=lambda: {
            "WHEAT": 10,
            "CARROT": 20,
            "TOMATO": 30,
            "STRAWBERRY": 50,
            "MELON": 80,
            "EGG": 30,
            "MILK": 50,
            "WOOL": 40,
            "FERTILIZER": 15,
        }
    )
    land_costs: dict[str, int] = field(
        default_factory=lambda: {"NE": 1000, "SW": 2000, "SE": 4000}
    )
    shed_capacity: int = 100
    min_cash_reserve: float = 500.0

    def evaluate(self, state: GameState) -> EconomicState:
        farm = state.farm
        market = state.market
        inventory = state.inventory
        season = state.season

        cash = farm.money
        shed_value = self._shed_value(inventory, market)
        seed_value = self._seed_value(state.private.get("seeds", {}))
        worker_count = len(farm.workers)
        worker_capacity = max(1, worker_count)

        land_tiles = self._count_tiles(farm)
        land_capacity = 100  # 10x10 grid
        animal_count, animal_capacity = self._count_animals(farm)

        prod_cap = self._production_capacity(farm, animal_count)
        exp_rev = self._expected_revenue(farm, market)
        exp_costs = self._expected_costs(farm, season)
        exp_profit = exp_rev - exp_costs

        opp_costs = self._opportunity_costs(state)
        market_cond = self._market_conditions(market)
        cap_reqs = self._capital_requirements(state)
        risk = self._risk_exposure(state)

        net_worth = cash + shed_value + seed_value
        expected_nw = net_worth + exp_profit
        potential_nw = self._potential_net_worth(state, market_cond)

        return EconomicState(
            cash=cash,
            shed_inventory_value=shed_value,
            seed_inventory_value=seed_value,
            production_capacity=prod_cap,
            worker_count=worker_count,
            worker_capacity=worker_capacity,
            land_tiles=land_tiles,
            land_capacity=land_capacity,
            animal_count=animal_count,
            animal_capacity=animal_capacity,
            expected_revenue=exp_rev,
            expected_costs=exp_costs,
            expected_profit=exp_profit,
            opportunity_costs=opp_costs,
            market_conditions=market_cond,
            remaining_turns=season.remaining_turns,
            capital_requirements=cap_reqs,
            risk_exposure=risk,
            net_worth=net_worth,
            expected_net_worth=expected_nw,
            potential_net_worth=potential_nw,
        )

    def _shed_value(self, inventory: Any, market: Any) -> float:
        total = 0.0
        for item, count in inventory.items().items():
            price = market.prices.get(item, self.base_prices.get(item, 1))
            total += count * price
        return total

    def _seed_value(self, seeds: dict[str, int]) -> float:
        total = 0.0
        for crop, count in seeds.items():
            price = self.base_prices.get(crop, 10)
            total += count * price
        return total

    def _count_tiles(self, farm: Any) -> int:
        unlocked = len(farm.quadrants) * 25
        return min(unlocked, 100)

    def _count_animals(self, farm: Any) -> tuple[int, int]:
        count = 0
        capacity = 0
        for tile in farm.tiles.values():
            if isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE"):
                if tile.get("animal") is not None:
                    count += 1
                    capacity += 1
                else:
                    capacity += 1
        return count, max(capacity, 1)

    def _production_capacity(self, farm: Any, animal_count: int) -> float:
        return float(animal_count)

    def _expected_revenue(self, farm: Any, market: Any) -> float:
        return 0.0

    def _expected_costs(self, farm: Any, season: Any) -> float:
        return 0.0

    def _opportunity_costs(self, state: GameState) -> dict[str, float]:
        return {}

    def _market_conditions(self, market: Any) -> dict[str, Any]:
        prices = dict(market.prices) if market.prices else {}
        inventory = dict(market.inventory) if market.inventory else {}
        return {
            "prices": prices,
            "inventory": inventory,
            "total_supply": sum(inventory.values()) if inventory else 0,
        }

    def _capital_requirements(self, state: GameState) -> dict[str, float]:
        reserved = 0.0
        return {"reserved": reserved}

    def _risk_exposure(self, state: GameState) -> float:
        return 0.0

    def _potential_net_worth(self, state: GameState, market_cond: dict) -> float:
        return state.farm.money + self._shed_value(state.inventory, state.market)
