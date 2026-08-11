"""Feature extraction must be fixed-length, deterministic, and public-only."""

from __future__ import annotations

import pytest

from agent.learning.features import (
    FEATURE_NAMES,
    FEATURE_VERSION,
    NUM_FEATURES,
    build_features,
    build_features_from_state,
    compact_state,
)
from agent.learning.schema import FEATURE_VERSION as SCHEMA_FEATURE_VERSION
from agent.runtime.game import GameSnapshot
from tests.fixtures.observations import (
    minimal_observation,
    observation_with_animal,
    observation_with_crop,
    observation_with_hands,
    observation_with_market,
    observation_with_quadrant,
    observation_with_shed,
)


def test_feature_vector_length() -> None:
    obs = minimal_observation()
    feats = build_features(GameSnapshot.from_obs(obs))
    assert len(feats) == NUM_FEATURES
    assert NUM_FEATURES == len(FEATURE_NAMES) == len(set(FEATURE_NAMES))


def test_feature_version_consistency() -> None:
    assert FEATURE_VERSION == SCHEMA_FEATURE_VERSION


def test_features_are_finite_floats() -> None:
    feats = build_features(GameSnapshot.from_obs(minimal_observation()))
    for value in feats:
        assert isinstance(value, float)
        assert value == value  # not NaN


def test_features_deterministic() -> None:
    snap = GameSnapshot.from_obs(minimal_observation())
    assert build_features(snap) == build_features(snap)


def test_compact_state_roundtrip() -> None:
    snap = GameSnapshot.from_obs(minimal_observation())
    state = compact_state(snap)
    assert build_features_from_state(state) == build_features(snap)


def test_feature_names_unique_and_stable() -> None:
    first = list(FEATURE_NAMES)
    assert first[0] == "day_norm"
    assert "money_norm" in first
    assert "opp_money_norm" in first
    assert "unlocked_norm" in first
    assert "hands_norm" in first


@pytest.mark.parametrize(
    "builder",
    [
        lambda: observation_with_crop(),
        lambda: observation_with_animal(),
        lambda: observation_with_hands(2),
        lambda: observation_with_market({"WHEAT": 12}),
        lambda: observation_with_quadrant(),
        lambda: observation_with_shed({"WHEAT": 5}),
    ],
)
def test_features_cover_varied_states(builder) -> None:
    obs = builder()
    feats = build_features(GameSnapshot.from_obs(obs))
    assert len(feats) == NUM_FEATURES
    assert all(v == v for v in feats)
