"""Integration tests for the full decision pipeline (chapter 9).

These tests verify the chain:
  Observation → ObservationAdapter → GameState → DecisionEngine → Strategy
  → Validation → ActionAdapter → KaggleAction
"""

from __future__ import annotations

import pytest

from agent.adapters.action_adapter import ActionAdapter
from agent.adapters.observation_adapter import ObservationAdapter
from agent.decision.decision_context import DecisionContext
from agent.decision.decision_engine import decide
from agent.observability import get_metrics
from tests.fixtures.observations import (
    minimal_observation,
    observation_advanced,
    observation_with_animal,
    observation_with_crop,
    observation_with_market,
    observation_with_seeds,
)


@pytest.fixture
def adapter() -> ObservationAdapter:
    return ObservationAdapter()


@pytest.fixture
def action_adapter() -> ActionAdapter:
    return ActionAdapter()


class TestFullPipeline:
    def test_observation_to_action(self, adapter, action_adapter) -> None:
        obs = minimal_observation()
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=obs["step"],
            day=obs["day"],
            hour=obs["hour"],
            remaining_turns=obs.get("remaining_turns", 720),
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert "farmer" in kaggle_action
        assert "hands" in kaggle_action
        assert "market" in kaggle_action

    def test_advanced_observation_to_action(self, adapter, action_adapter) -> None:
        obs = observation_advanced(day=10, money=5000.0)
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=obs["step"],
            day=obs["day"],
            hour=obs["hour"],
            remaining_turns=obs.get("remaining_turns", 720),
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert isinstance(kaggle_action["farmer"], list)

    def test_with_crop_observation_to_action(self, adapter, action_adapter) -> None:
        obs = observation_with_crop("WHEAT", planted_day=2)
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=obs["step"],
            day=obs["day"],
            hour=obs["hour"],
            remaining_turns=obs.get("remaining_turns", 720),
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert isinstance(kaggle_action["farmer"], list)

    def test_with_seeds_observation_to_action(self, adapter, action_adapter) -> None:
        obs = observation_with_seeds({"WHEAT": 5})
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=obs["step"],
            day=obs["day"],
            hour=obs["hour"],
            remaining_turns=obs.get("remaining_turns", 720),
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert isinstance(kaggle_action, dict)


class TestPipelineWithMarket:
    def test_market_observation_to_action(self, adapter, action_adapter) -> None:
        obs = observation_with_market(
            {"WHEAT": 25, "CARROT": 35, "STRAWBERRY": 75},
            {"WHEAT": 5000, "CARROT": 3000, "STRAWBERRY": 1000},
        )
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=2,
            day=0,
            hour=2,
            remaining_turns=718,
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert "farmer" in kaggle_action


class TestPipelineWithAnimals:
    def test_animal_observation_to_action(self, adapter, action_adapter) -> None:
        obs = observation_with_animal("GOOSE")
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=3,
            day=0,
            hour=3,
            remaining_turns=717,
            strategy_name="baseline",
        )
        domain_action = decide(context)
        kaggle_action = action_adapter.convert(domain_action)
        assert isinstance(kaggle_action["farmer"], list)


class TestPipelineObservability:
    def test_decision_records_metrics(self, adapter, action_adapter) -> None:
        metrics = get_metrics()
        initial_count = metrics.counter("decision_count")
        obs = minimal_observation()
        game_state = adapter.parse(obs)
        context = DecisionContext(
            obs=obs,
            player=0,
            game_state=game_state,
            step=0,
            day=0,
            hour=0,
            strategy_name="baseline",
        )
        decide(context)
        assert metrics.counter("decision_count") == initial_count + 1
