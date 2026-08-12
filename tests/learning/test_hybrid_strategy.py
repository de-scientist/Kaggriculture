"""Tests for the Stage 3 hybrid strategy (learned + champion + safety)."""

from __future__ import annotations

from typing import Any

import pytest

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.learning.features import FEATURE_VERSION, NUM_FEATURES
from agent.learning.models.bundle import LearnedBundle
from agent.learning.models.policy_model import SoftmaxPolicyModel
from agent.learning.models.scaler import FeatureScaler
from agent.learning.models.value_model import LinearValueModel
from agent.strategies.hybrid_strategy import HybridStrategy
from tests.fixtures.observations import minimal_observation


def _ready_bundle(prefer: str = "plant") -> LearnedBundle:
    n = NUM_FEATURES
    classes = ["plant", "harvest", "water", "pass"]
    weights = [[2.0 if c == prefer else 0.0] * n for c in classes]
    return LearnedBundle(
        value=LinearValueModel(weights=[0.0] * n, bias=0.0),
        policy=SoftmaxPolicyModel(classes=classes, weights=weights, bias=[0.0] * 4),
        scaler=FeatureScaler(means=[0.0] * n, stds=[1.0] * n),
        feature_version=FEATURE_VERSION,
        model_id="test-bundle",
    )


def _context() -> DecisionContext:
    return DecisionContext(
        obs=minimal_observation(),
        player=0,
        step=0,
        day=0,
        remaining_turns=720,
        strategy_name="hybrid",
    )


def _candidates() -> list[CandidateAction]:
    return [
        CandidateAction(id="plant1", action_type="plant", estimated_cost=10.0, estimated_reward=20.0),
        CandidateAction(id="pass1", action_type="pass", estimated_cost=0.0, estimated_reward=0.0),
    ]


def test_champion_fallback_when_no_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agent.strategies.hybrid_strategy.load_latest_bundle",
        lambda: LearnedBundle.placeholder(),
    )
    strategy = HybridStrategy()
    scored = strategy.evaluate(_context(), _candidates())
    assert len(scored) == 2
    assert strategy.last_decision["mode"] == "champion"
    assert strategy.last_decision["reason"] == "no_ready_model"


def test_hybrid_trusts_confident_learned_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agent.strategies.hybrid_strategy.load_latest_bundle",
        _ready_bundle,
    )
    strategy = HybridStrategy(confidence_threshold=0.5, learned_weight=0.7)
    scored = strategy.evaluate(_context(), _candidates())
    assert strategy.last_decision["mode"] == "hybrid"
    assert scored[0].action.id == "plant1"


def test_low_confidence_defers_to_champion(monkeypatch: pytest.MonkeyPatch) -> None:
    # All-equal weights -> uniform probabilities -> low confidence.
    n = NUM_FEATURES
    flat = LearnedBundle(
        value=LinearValueModel(weights=[0.0] * n, bias=0.0),
        policy=SoftmaxPolicyModel(
            classes=["plant", "harvest", "water", "pass"],
            weights=[[0.0] * n for _ in range(4)],
            bias=[0.0] * 4,
        ),
        scaler=FeatureScaler(means=[0.0] * n, stds=[1.0] * n),
        feature_version=FEATURE_VERSION,
    )
    monkeypatch.setattr(
        "agent.strategies.hybrid_strategy.load_latest_bundle", lambda: flat
    )
    strategy = HybridStrategy(confidence_threshold=0.5)
    strategy.evaluate(_context(), _candidates())
    assert strategy.last_decision["mode"] == "champion"
    assert strategy.last_decision["reason"] == "low_confidence"


def test_economic_sanity_rejects_unaffordable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "agent.strategies.hybrid_strategy.load_latest_bundle",
        _ready_bundle,
    )
    candidates = [
        CandidateAction(id="buy", action_type="buy_land", estimated_cost=99999.0, estimated_reward=0.0),
        CandidateAction(id="plant1", action_type="plant", estimated_cost=10.0, estimated_reward=20.0),
    ]
    strategy = HybridStrategy(confidence_threshold=0.5, learned_weight=0.9)
    scored = strategy.evaluate(_context(), candidates)
    assert scored[-1].action.id == "buy"


def test_empty_actions_return_unchanged() -> None:
    strategy = HybridStrategy()
    assert strategy.evaluate(_context(), []) == []
