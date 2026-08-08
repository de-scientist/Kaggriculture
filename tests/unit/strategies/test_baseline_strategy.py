"""Unit tests for the Strategy layer (chapter 9)."""
from __future__ import annotations

import pytest

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies import baseline_strategy
from agent.strategies.priorities import PRIORITY_HARVEST, PRIORITY_IDLE, get_priority
from agent.strategies.scoring import score_action
from tests.fixtures.observations import minimal_observation
from tests.fixtures.game_states import empty_game_state


@pytest.fixture
def context() -> DecisionContext:
    return DecisionContext(
        obs=minimal_observation(),
        player=0,
        game_state=empty_game_state(),
        step=0,
        day=0,
        hour=0,
        strategy_name="baseline",
    )


def _make_action(action_id: str, action_type: str, **kwargs) -> CandidateAction:
    return CandidateAction(id=action_id, action_type=action_type, **kwargs)


class TestPriorities:
    @pytest.mark.parametrize("action_type,expected", [
        ("harvest", 1),
        ("collect", 2),
        ("feed", 3),
        ("water", 4),
        ("fertilize", 5),
        ("plant", 6),
        ("sell", 7),
        ("buy", 8),
        ("hire", 9),
        ("expand", 10),
        ("pass", 11),
        ("unknown", 11),
    ])
    def test_get_priority(self, action_type: str, expected: int) -> None:
        assert get_priority(action_type) == expected

    def test_priority_constants(self) -> None:
        assert PRIORITY_HARVEST == 1
        assert PRIORITY_IDLE == 11


class TestScoring:
    def test_score_pass_action(self) -> None:
        action = _make_action("pass", "pass")
        score, explanation = score_action(action)
        assert isinstance(score, float)
        assert isinstance(explanation, str)

    def test_score_profit_action(self) -> None:
        action = _make_action("sell", "sell", estimated_reward=20.0)
        score, explanation = score_action(action)
        assert score > 0

    def test_score_cost_penalty(self) -> None:
        cheap = _make_action("a", "plant", estimated_cost=1.0, estimated_reward=0.0)
        expensive = _make_action("b", "plant", estimated_cost=100.0, estimated_reward=0.0)
        score_cheap, _ = score_action(cheap)
        score_expensive, _ = score_action(expensive)
        assert score_expensive < score_cheap

    def test_score_harvest_higher_than_water(self) -> None:
        harvest = _make_action("h", "harvest", estimated_reward=10.0)
        water = _make_action("w", "water", estimated_reward=5.0)
        score_harvest, _ = score_action(harvest)
        score_water, _ = score_action(water)
        assert score_harvest > score_water


class TestBaselineStrategy:
    def test_is_strategy_subclass(self) -> None:
        s = baseline_strategy.BaselineStrategy()
        from agent.strategies.strategy import Strategy
        assert isinstance(s, Strategy)

    def test_evaluate_returns_scored_actions(self, context: DecisionContext) -> None:
        strategy = baseline_strategy.BaselineStrategy()
        actions = [
            _make_action("a", "pass", estimated_reward=0.0),
            _make_action("b", "harvest", estimated_reward=10.0),
        ]
        scored = strategy.evaluate(context, actions)
        assert len(scored) == 2

    def test_evaluate_sorts_by_score(self, context: DecisionContext) -> None:
        strategy = baseline_strategy.BaselineStrategy()
        actions = [
            _make_action("low", "pass", estimated_reward=0.0),
            _make_action("high", "harvest", estimated_reward=50.0, estimated_cost=0.0),
        ]
        scored = strategy.evaluate(context, actions)
        assert scored[0].action.action_type == "harvest"
        assert scored[1].action.action_type == "pass"

    def test_evaluate_deterministic(self, context: DecisionContext) -> None:
        strategy = baseline_strategy.BaselineStrategy()
        actions = [
            _make_action("a", "pass"),
            _make_action("b", "plant"),
        ]
        first = strategy.evaluate(context, actions)
        second = strategy.evaluate(context, actions)
        assert [s.action.id for s in first] == [s.action.id for s in second]
