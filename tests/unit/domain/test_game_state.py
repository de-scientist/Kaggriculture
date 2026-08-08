"""Unit tests for the GameState domain model (chapter 9)."""
from __future__ import annotations

from agent.domain.farm import Farm
from agent.domain.game_state import GameState
from agent.domain.inventory import Inventory
from agent.domain.market import Market
from agent.domain.position import Position
from agent.domain.season import Season
from agent.domain.worker import Worker


class TestGameStateConstruction:
    def test_defaults(self) -> None:
        state = GameState(player=0)
        assert state.player == 0
        assert state.current_day() == 0
        assert state.current_turn() == 0
        assert state.remaining_turns() == 720
        assert state.remaining_days() == 30
        assert state.available_money() == 3000.0
        assert len(state.available_workers()) == 0

    def test_custom_state(self) -> None:
        farm = Farm(money=5000.0)
        inventory = Inventory().add("WHEAT", 10)
        market = Market(prices={"WHEAT": 25})
        season = Season(day=5, turn=120)
        state = GameState(
            player=0,
            farm=farm,
            inventory=inventory,
            market=market,
            season=season,
            step=120,
        )
        assert state.current_day() == 5
        assert state.current_turn() == 120
        assert state.available_money() == 5000.0


class TestGameStateAdvancement:
    def test_advance_turn(self) -> None:
        state = GameState(player=0, step=5)
        advanced = state.advance_turn()
        assert advanced.step == 6

    def test_advance_turn_at_day_boundary(self) -> None:
        state = GameState(player=0, step=23)
        advanced = state.advance_turn()
        assert advanced.step == 24
        assert advanced.current_day() == 1

    def test_advance_returns_new_instance(self) -> None:
        state = GameState(player=0, step=5)
        advanced = state.advance_turn()
        assert state is not advanced
        assert state.step == 5
        assert advanced.step == 6


class TestGameStateQueries:
    def test_available_money(self) -> None:
        farm = Farm(money=4500.0)
        state = GameState(player=0, farm=farm)
        assert state.available_money() == 4500.0

    def test_available_workers(self) -> None:
        farm = Farm(workers=[
            Worker(worker_id="farmer", position=Position(0, 0)),
            Worker(worker_id="hand1", position=Position(1, 0)),
        ])
        state = GameState(player=0, farm=farm)
        assert len(state.available_workers()) == 2

    def test_current_market(self) -> None:
        market = Market(prices={"WHEAT": 25})
        state = GameState(player=0, market=market)
        assert state.current_market() is market
