"""Tests for the Stage 4 endgame policy (horizon-dependent wind-down)."""

from __future__ import annotations

from agent.runtime.game import GameSnapshot
from agent.runtime.policies import ChampionPolicy, EndgamePolicy
from agent.runtime.settings import RuntimeSettings
from tests.fixtures.observations import minimal_observation


def _snapshot(day: int) -> GameSnapshot:
    obs = minimal_observation()
    obs["day"] = day
    return GameSnapshot.from_obs(obs)


def test_endgame_liquidates_near_horizon() -> None:
    policy = EndgamePolicy()
    settings = RuntimeSettings()
    adjusted, info = policy.adjust(_snapshot(27), settings)
    assert info["mode"] == "endgame_liquidate"
    assert adjusted.plant_enabled is False
    assert adjusted.target_hands == (0, 0, 0, 0)
    assert adjusted.land_latest_day == (0, 0, 0)
    assert adjusted.enable_animals is False


def test_endgame_winds_down_in_final_week() -> None:
    policy = EndgamePolicy()
    settings = RuntimeSettings()
    adjusted, info = policy.adjust(_snapshot(23), settings)
    assert info["mode"] == "endgame_wind_down"
    assert adjusted.plant_enabled is True
    assert adjusted.land_latest_day == (0, 0, 0)
    assert adjusted.target_hands == (2, 2, 2, 2)


def test_endgame_is_champion_early() -> None:
    policy = EndgamePolicy()
    settings = RuntimeSettings()
    adjusted, info = policy.adjust(_snapshot(5), settings)
    assert info["mode"] == "champion"
    assert adjusted is settings  # unchanged early game
    assert isinstance(policy, ChampionPolicy)
