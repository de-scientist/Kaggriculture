"""Tests for the Stage 3 self-play / tournament framework."""

from __future__ import annotations

from typing import Any

from agent.evaluation.tournament import (
    Agent,
    run_match,
    run_tournament,
)


def _stub_simulator(wins_a: float, wins_b: float):
    def _run(agent_a: Agent, agent_b: Agent) -> tuple[float, float]:
        return wins_a, wins_b

    return _run


def _pass_agent(obs: dict[str, Any]) -> dict[str, Any]:
    return {"farmer": ["PASS"], "hands": [], "market": []}


def test_run_match_reports_winner() -> None:
    result = run_match(
        _pass_agent, _pass_agent, simulator=_stub_simulator(100.0, 50.0)
    )
    assert result.reward_a == 100.0
    assert result.reward_b == 50.0
    assert result.winner == 0
    assert result.margin == 50.0


def test_run_match_tie() -> None:
    result = run_match(
        _pass_agent, _pass_agent, simulator=_stub_simulator(10.0, 10.0)
    )
    assert result.winner == -1


def test_run_tournament_standings() -> None:
    agents: dict[str, Agent] = {"champion": _pass_agent, "challenger": _pass_agent}
    result = run_tournament(
        agents, episodes=2, simulator=_stub_simulator(80.0, 40.0)
    )
    assert len(result.matches) == 2
    # With the stub, "A" (first-listed) always wins.
    assert result.standings()[0][0] == "champion"
    assert result.wins("champion") == 2
    assert result.wins("challenger") == 0


def test_run_tournament_avg_reward() -> None:
    agents: dict[str, Agent] = {"a": _pass_agent, "b": _pass_agent}
    result = run_tournament(
        agents, episodes=3, simulator=_stub_simulator(60.0, 20.0)
    )
    assert result.avg_reward("a") == 60.0
    assert result.avg_reward("b") == 20.0
