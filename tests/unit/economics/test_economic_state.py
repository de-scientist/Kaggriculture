"""Unit tests for the Economic State Model (Stage 2)."""

from __future__ import annotations

from agent.domain.farm import Farm
from agent.domain.game_state import GameState
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.economics.economic_state import EconomicEvaluator, EconomicState


class TestEconomicStateConstruction:
    def test_default_values(self) -> None:
        state = EconomicState(
            cash=3000.0,
            shed_inventory_value=0.0,
            seed_inventory_value=0.0,
            production_capacity=0.0,
            worker_count=1,
            worker_capacity=1,
            land_tiles=25,
            land_capacity=100,
            animal_count=0,
            animal_capacity=0,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions={},
            remaining_turns=720,
            capital_requirements={},
            risk_exposure=0.0,
            net_worth=3000.0,
            expected_net_worth=3000.0,
            potential_net_worth=3000.0,
        )
        assert state.cash == 3000.0
        assert state.net_worth == 3000.0
        assert state.profit_per_turn == 0.0

    def test_available_capital(self) -> None:
        state = EconomicState(
            cash=3000.0,
            shed_inventory_value=0.0,
            seed_inventory_value=0.0,
            production_capacity=0.0,
            worker_count=1,
            worker_capacity=1,
            land_tiles=25,
            land_capacity=100,
            animal_count=0,
            animal_capacity=0,
            expected_revenue=0.0,
            expected_costs=0.0,
            expected_profit=0.0,
            opportunity_costs={},
            market_conditions={},
            remaining_turns=720,
            capital_requirements={"reserved": 500.0},
            risk_exposure=0.0,
            net_worth=3000.0,
            expected_net_worth=3000.0,
            potential_net_worth=3000.0,
        )
        assert state.available_capital == 2500.0


class TestEconomicEvaluator:
    def test_evaluate_minimal_state(self) -> None:
        state = GameState(player=0, step=0)
        evaluator = EconomicEvaluator()
        econ = evaluator.evaluate(state)
        assert isinstance(econ, EconomicState)
        assert econ.cash == 3000.0
        assert econ.remaining_turns == 720

    def test_evaluate_with_money(self) -> None:
        farm = Farm(money=5000.0)
        state = GameState(player=0, farm=farm, step=0)
        evaluator = EconomicEvaluator()
        econ = evaluator.evaluate(state)
        assert econ.cash == 5000.0

    def test_net_worth_includes_shed_value(self) -> None:
        inventory = Inventory()
        inventory = inventory.add("WHEAT", 10)
        farm = Farm(money=3000.0)
        market = Market(prices={"WHEAT": 15})
        state = GameState(player=0, farm=farm, inventory=inventory, market=market, step=0)
        evaluator = EconomicEvaluator()
        econ = evaluator.evaluate(state)
        assert econ.net_worth == 3000.0 + 10 * 15
