"""Determinism and reproducibility tests (chapter 9 §212-213).

Verifies that identical observations produce identical decisions when
the random seed is fixed, and that results are reproducible across
multiple runs.
"""

from __future__ import annotations

from typing import Any

from agent.agent import agent
from tests.fixtures.observations import minimal_observation


class TestDeterminism:
    def test_identical_observations_produce_identical_actions(self) -> None:
        obs = minimal_observation()
        obs["step"] = 0

        first = agent(dict(obs))
        second = agent(dict(obs))

        assert first == second

    def test_actions_consistent_across_steps(self) -> None:
        results = []
        for _ in range(3):
            actions = []
            for step in range(10):
                obs = dict(minimal_observation())
                obs["step"] = step
                actions.append(agent(obs))
            results.append(actions)

        for i in range(1, len(results)):
            assert results[i] == results[0], f"Run {i} diverged from run 0"

    def test_full_episode_deterministic(self) -> None:
        def run_episode() -> list[dict[str, Any]]:
            actions = []
            for step in range(50):
                obs = dict(minimal_observation())
                obs["step"] = step
                obs["day"] = step // 24
                obs["hour"] = step % 24
                actions.append(agent(obs))
            return actions

        first = run_episode()
        second = run_episode()
        assert first == second, "Episode not deterministic across runs"
