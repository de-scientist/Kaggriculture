"""Unit tests for the decision engine components (chapter 9)."""
from __future__ import annotations

import pytest

from agent.decision.action_filter import filter_pre_validation
from agent.decision.action_generator import generate_candidates
from agent.decision.action_ranker import rank, resolve_ties
from agent.decision.action_validator import validate_action, validate_actions
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.decision.decision_engine import decide
from agent.decision.fallback import get_fallback
from tests.fixtures.game_states import empty_game_state
from tests.fixtures.observations import minimal_observation


@pytest.fixture
def context() -> DecisionContext:
    settings = {
        "strategy": {"name": "baseline"},
        "seed": 42,
    }
    return DecisionContext(
        obs=minimal_observation(),
        player=0,
        game_state=empty_game_state(),
        config=settings,
        step=0,
        day=0,
        hour=0,
        remaining_turns=720,
        strategy_name="baseline",
    )


class TestCandidateAction:
    def test_net_value(self) -> None:
        action = CandidateAction(
            id="test",
            action_type="plant",
            estimated_cost=10.0,
            estimated_reward=25.0,
        )
        assert action.net_value == 15.0

    def test_net_value_negative(self) -> None:
        action = CandidateAction(
            id="test",
            action_type="pass",
            estimated_cost=50.0,
            estimated_reward=0.0,
        )
        assert action.net_value == -50.0

    def test_defaults(self) -> None:
        action = CandidateAction(id="test", action_type="pass")
        assert action.target_entity == ""
        assert action.target_position is None
        assert action.worker == ""
        assert action.estimated_cost == 0.0
        assert action.estimated_reward == 0.0
        assert action.metadata == {}


class TestActionGenerator:
    def test_generates_candidates(self, context: DecisionContext) -> None:
        candidates = generate_candidates(context)
        assert len(candidates) > 0
        assert all(isinstance(c, CandidateAction) for c in candidates)

    def test_includes_pass_candidate(self, context: DecisionContext) -> None:
        candidates = generate_candidates(context)
        pass_types = [c for c in candidates if c.action_type == "pass"]
        assert len(pass_types) > 0


class TestActionFilter:
    def test_filter_by_resources(self) -> None:
        actions = [
            CandidateAction(id="cheap", action_type="pass", estimated_cost=10.0),
            CandidateAction(id="expensive", action_type="buy", estimated_cost=100.0),
        ]
        result = filter_pre_validation(actions, available_money=50.0, available_workers=1, owned_tiles=set())
        ids = [a.id for a in result]
        assert "cheap" in ids
        assert "expensive" not in ids

    def test_filter_by_worker_availability(self) -> None:
        actions = [
            CandidateAction(id="pass", action_type="pass"),
            CandidateAction(id="plant", action_type="plant"),
        ]
        result = filter_pre_validation(actions, available_money=100.0, available_workers=0, owned_tiles=set())
        ids = [a.action_type for a in result]
        assert "pass" in ids
        assert "plant" not in ids

    def test_filter_by_ownership(self) -> None:
        actions = [
            CandidateAction(id="a1", action_type="harvest", target_position=(0, 0)),
            CandidateAction(id="a2", action_type="plant", target_position=(5, 5)),
        ]
        owned = {(0, 0), (0, 1)}
        result = filter_pre_validation(actions, available_money=100.0, available_workers=1, owned_tiles=owned)
        ids = [a.id for a in result]
        assert "a1" in ids
        assert "a2" not in ids

    def test_filter_actions_with_no_target_position(self) -> None:
        actions = [
            CandidateAction(id="a1", action_type="sell"),
            CandidateAction(id="a2", action_type="pass"),
        ]
        result = filter_pre_validation(actions, available_money=100.0, available_workers=1, owned_tiles=set())
        assert len(result) == 2


class TestActionValidator:
    def test_valid_action(self) -> None:
        action = CandidateAction(id="test", action_type="pass")
        result = validate_action(action, None)
        assert result.is_valid is True

    def test_plant_action_requires_target_position(self) -> None:
        action = CandidateAction(id="test", action_type="plant")
        result = validate_action(action, None)
        assert result.is_valid is False
        assert any("Target position" in r for r in result.failure_reasons)

    def test_buy_action_validates_funds(self) -> None:
        state = empty_game_state()
        action = CandidateAction(id="test", action_type="buy_seed", estimated_cost=100.0)
        result = validate_action(action, state)
        assert result.is_valid is True

    def test_buy_action_insufficient_funds(self) -> None:
        state = empty_game_state(player=0)
        action = CandidateAction(
            id="test", action_type="buy_seed", estimated_cost=99999.0
        )
        result = validate_action(action, state)
        assert result.is_valid is False
        assert any("Insufficient" in r for r in result.failure_reasons)

    def test_hire_action_max_reached(self) -> None:
        from agent.domain.farm import Farm
        from agent.domain.position import Position
        from agent.domain.worker import Worker

        farm = Farm(workers=[Worker(worker_id="farmer", position=Position(0, 0))], money=10000.0)
        farm = farm.add_quadrant("NE")
        state = empty_game_state()
        state = type(state)(
            player=state.player, farm=farm, inventory=state.inventory,
            market=state.market, step=state.step,
        )

    def test_validate_actions_list(self) -> None:
        actions = [
            CandidateAction(id="a1", action_type="pass"),
            CandidateAction(id="a2", action_type="plant"),
        ]
        results = validate_actions(actions, None)
        assert results[0].is_valid is True
        assert results[1].is_valid is False


class TestActionRanker:
    def test_rank_sorts_by_utility(self) -> None:
        actions = [
            CandidateAction(id="low", action_type="water", estimated_cost=0.0, estimated_reward=1.0),
            CandidateAction(id="high", action_type="harvest", estimated_cost=0.0, estimated_reward=10.0),
        ]
        ranked = rank(actions, None)
        assert ranked[0].id == "high"
        assert ranked[1].id == "low"

    def test_resolve_ties_sorts_by_id(self) -> None:
        actions = [
            CandidateAction(id="zebra", action_type="pass", estimated_cost=0.0, estimated_reward=0.0),
            CandidateAction(id="alpha", action_type="pass", estimated_cost=0.0, estimated_reward=0.0),
        ]
        resolved = resolve_ties(actions)
        assert resolved[0].id == "alpha"
        assert resolved[1].id == "zebra"


class TestFallback:
    def test_fallback_returns_pass(self) -> None:
        fallback = get_fallback()
        assert fallback.action_type == "pass"
        assert fallback.estimated_cost == 0.0
        assert fallback.metadata.get("fallback") is True


class TestDecisionEngine:
    def test_decide_returns_valid_action(self, context: DecisionContext) -> None:
        action = decide(context)
        assert "farmer" in action
        assert "hands" in action
        assert "market" in action
        assert isinstance(action["farmer"], list)
        assert isinstance(action["hands"], list)
        assert isinstance(action["market"], list)

    def test_decide_returns_pass_for_empty_context(self) -> None:
        ctx = DecisionContext(obs={}, player=0)
        action = decide(ctx)
        assert action["farmer"] == ["PASS"]
