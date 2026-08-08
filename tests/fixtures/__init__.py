"""Shared test fixtures for the Kaggriculture AI test suite.

This package centralises reusable observation, game-state, market, farm,
action, and episode fixtures so that every test layer (unit, integration,
end-to-end, regression) draws from a single, deterministic source of truth.
"""
from tests.fixtures import actions, episodes, farms, game_states, markets, observations

__all__ = [
    "actions",
    "episodes",
    "farms",
    "game_states",
    "markets",
    "observations",
]
