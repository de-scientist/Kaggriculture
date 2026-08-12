"""End-to-end test: the public ``agent(obs)`` entry point."""

from __future__ import annotations

import logging

from agent.agent import agent
from agent.config import reset_config
from agent.observability import get_metrics, get_replay_store, get_telemetry

OBS = {
    "player": 0,
    "step": 1,
    "day": 0,
    "hour": 0,
    "remaining_turns": 720,
    "farms": [
        {
            "money": 3000,
            "tiles": [[None]],
            "farmer": [0, 0],
            "hands": [],
            "unlocked_quadrants": ["NW"],
            "hires_today": 0,
        },
        {
            "money": 3000,
            "tiles": [[None]],
            "farmer": [0, 0],
            "hands": [],
            "unlocked_quadrants": ["NW"],
            "hires_today": 0,
        },
    ],
    "private": {"shed": {}, "seeds": {}, "inventories": [{}]},
    "market": {"inventory": {}, "prices": {}},
    "town": {"unlocked_shops": []},
}


def test_agent_returns_valid_action_dict() -> None:
    reset_config()
    logging.disable(logging.CRITICAL)
    action = agent(OBS)
    logging.disable(logging.NOTSET)
    assert set(action) == {"farmer", "hands", "market"}
    assert isinstance(action["farmer"], list)
    assert action["farmer"]  # non-empty op list
    assert isinstance(action["hands"], list)
    assert isinstance(action["market"], list)


def test_agent_records_observability_for_first_turn() -> None:
    reset_config()
    logging.disable(logging.CRITICAL)
    action = agent(OBS)
    logging.disable(logging.NOTSET)
    assert get_telemetry().decisions >= 1
    assert get_metrics().counter("decision_count") >= 1.0
    assert len(get_replay_store().records()) >= 1


def test_agent_falls_back_to_pass_on_malformed_obs() -> None:
    reset_config()
    logging.disable(logging.CRITICAL)
    # Missing 'player' and malformed farms -> parse or decide must not crash.
    action = agent({"step": 0, "day": 0, "hour": 0})
    logging.disable(logging.NOTSET)
    assert action == {"farmer": ["PASS"], "hands": [], "market": []}
