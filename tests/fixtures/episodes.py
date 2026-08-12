"""Shared episode fixtures for end-to-end and regression tests."""

from __future__ import annotations

from typing import Any

from tests.fixtures.observations import minimal_observation


def episode_initial() -> list[dict[str, Any]]:
    """A single-turn episode observation (start of game)."""
    return [minimal_observation()]


def episode_short() -> list[dict[str, Any]]:
    """A 5-turn mini episode for e2e tests."""
    obs = minimal_observation()
    observations = []
    for step in range(5):
        o = dict(obs)
        o["step"] = step
        o["day"] = 0
        o["hour"] = step
        observations.append(o)
    return observations


def episode_multi_day(n_days: int = 3) -> list[dict[str, Any]]:
    """An episode spanning multiple days."""
    obs = minimal_observation()
    observations = []
    for day in range(n_days):
        for hour in range(24):
            o = dict(obs)
            o["step"] = day * 24 + hour
            o["day"] = day
            o["hour"] = hour
            observations.append(o)
    return observations


def episode_with_crop_lifecycle() -> list[dict[str, Any]]:
    """An episode simulating plant → water → grow → harvest → sell."""
    observations = []
    base = minimal_observation()

    obs = dict(base)
    observations.append(obs)

    obs = dict(base)
    obs["private"] = {"shed": {"WHEAT": 1}, "seeds": {"WHEAT": 1}, "inventories": [{}]}
    observations.append(obs)

    obs = dict(base)
    obs["step"] = 2
    observations.append(obs)

    return observations
