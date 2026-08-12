"""Tests for the Stage 3 safe exploration policy."""

from __future__ import annotations

from typing import Any

import pytest

from agent.learning.exploration import ExplorationConfig, ExplorationPolicy


def test_explores_when_epsilon_one() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=1.0, seed=7))
    policy.reset(100)
    options = ["a", "b", "c"]
    scores = [3.0, 1.0, 1.0]
    chosen, explored = policy.select(
        options, scores, remaining_turns=100, confidence=0.0, step=0
    )
    assert explored is True
    assert chosen in options


def test_exploits_when_epsilon_zero() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=0.0, seed=7))
    policy.reset(100)
    options = ["a", "b", "c"]
    scores = [3.0, 1.0, 1.0]
    chosen, explored = policy.select(
        options, scores, remaining_turns=100, confidence=0.0, step=0
    )
    assert explored is False
    assert chosen == "a"


def test_no_exploration_near_endgame() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=1.0, min_remaining_turns=50))
    policy.reset(100)
    options = ["a", "b"]
    scores = [1.0, 1.0]
    _, explored = policy.select(
        options, scores, remaining_turns=10, confidence=0.0, step=0
    )
    assert explored is False


def test_no_exploration_when_confident() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=1.0, high_confidence_skip=0.9))
    policy.reset(100)
    options = ["a", "b"]
    scores = [1.0, 1.0]
    _, explored = policy.select(
        options, scores, remaining_turns=100, confidence=0.95, step=0
    )
    assert explored is False


def test_budget_is_respected() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=1.0, max_exploration_fraction=0.0))
    policy.reset(100)
    options = ["a", "b"]
    scores = [1.0, 1.0]
    _, explored = policy.select(
        options, scores, remaining_turns=100, confidence=0.0, step=0
    )
    assert explored is False


def test_uncertainty_sample_picks_highest_uncertainty() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig(epsilon=1.0, seed=3))
    policy.reset(100)
    options = ["a", "b", "c"]
    uncertainties = [0.1, 0.9, 0.5]
    chosen, explored = policy.uncertainty_sample(options, uncertainties)
    assert explored is True
    assert chosen == "b"


def test_select_requires_matching_lengths() -> None:
    policy: ExplorationPolicy[Any] = ExplorationPolicy(ExplorationConfig())
    policy.reset(10)
    with pytest.raises(ValueError):
        policy.select(["a"], [1.0, 2.0], remaining_turns=100, confidence=0.0, step=0)
