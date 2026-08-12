"""End-to-end full episode tests (chapter 9).

Runs the agent over a complete simulated episode (or a truncated version)
to verify initialization, observation processing, decision making, action
validity, state progression, and absence of fatal exceptions.
"""

from __future__ import annotations

from agent.agent import agent
from agent.observability import get_metrics, get_telemetry
from tests.fixtures.observations import (
    minimal_observation,
    observation_advanced,
    observation_with_crop,
    observation_with_seeds,
)


def _run_episode(observations: list[dict]) -> list[dict]:
    actions = []
    for obs in observations:
        action = agent(obs)
        actions.append(action)
    return actions


class TestFullEpisode:
    def test_agent_initializes(self, reset_singletons) -> None:
        obs = minimal_observation()
        action = agent(obs)
        assert isinstance(action, dict)
        assert "farmer" in action
        assert "hands" in action
        assert "market" in action

    def test_first_decision_is_valid(self, reset_singletons) -> None:
        obs = minimal_observation()
        action = agent(obs)
        assert isinstance(action["farmer"], list)
        assert len(action["farmer"]) > 0
        assert action["farmer"][0] in (
            "PASS",
            "NORTH",
            "SOUTH",
            "EAST",
            "WEST",
            "PLANT",
            "WATER",
            "HARVEST",
            "FERTILIZE",
            "DIG",
            "BUILD_COOP",
            "BUILD_PASTURE",
            "FEED",
            "COLLECT_FERTILIZER",
            "CARE",
            "PICKUP",
            "PLACE",
            "DROP",
        )

    def test_no_crashes_over_episode(self, reset_singletons) -> None:
        observations = []
        for step in range(50):
            obs = minimal_observation()
            obs["step"] = step
            obs["day"] = step // 24
            obs["hour"] = step % 24
            observations.append(obs)

        actions = _run_episode(observations)
        assert len(actions) == 50
        for action in actions:
            assert "farmer" in action
            assert "hands" in action
            assert "market" in action

    def test_advanced_episode(self, reset_singletons) -> None:
        observations = []
        for step in range(24):
            obs = observation_advanced(day=1, money=3500.0)
            obs["step"] = step + 24
            obs["hour"] = step
            observations.append(obs)

        actions = _run_episode(observations)
        assert len(actions) == 24
        for action in actions:
            assert "farmer" in action

    def test_full_720_turn_episode_completes(self, reset_singletons) -> None:
        observations = []
        for step in range(720):
            obs = minimal_observation()
            obs["step"] = step
            obs["day"] = step // 24
            obs["hour"] = step % 24
            observations.append(obs)

        actions = _run_episode(observations)
        assert len(actions) == 720

    def test_episode_records_observability(self, reset_singletons) -> None:
        obs = minimal_observation()
        obs["step"] = 0
        agent(obs)
        metrics = get_metrics()
        telemetry = get_telemetry()
        assert metrics.counter("decision_count") >= 1.0
        assert telemetry.decisions >= 1


class TestEpisodeLifecycle:
    def test_crop_lifecycle_observation(self, reset_singletons) -> None:
        obs = observation_with_crop("WHEAT", planted_day=2)
        action = agent(obs)
        assert "farmer" in action

    def test_seed_purchase_observation(self, reset_singletons) -> None:
        obs = observation_with_seeds({"WHEAT": 0})
        obs["farms"][0]["money"] = 5000.0
        action = agent(obs)
        assert "farmer" in action

    def test_malformed_observation_falls_back(self, reset_singletons) -> None:
        obs = {"player": 0}
        action = agent(obs)
        assert action == {"farmer": ["PASS"], "hands": [], "market": []}
