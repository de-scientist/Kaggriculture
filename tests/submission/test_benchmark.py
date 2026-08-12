"""Tests for the Stage 4B benchmark infrastructure (no Kaggle runtime needed)."""

from __future__ import annotations

from typing import Any

from agent.evaluation.benchmark_runner import BenchmarkRunner, MetricsAgent, _SimResult
from agent.evaluation.metrics import (
    BenchmarkSummary,
    MatchMetrics,
    OpponentSummary,
    winner_from_rewards,
)
from agent.submission.failsafe import EMERGENCY_ACTION, FailSafeAgent


def _fake_simulator(coins: float = 20000.0, opp: float = 3000.0) -> Any:
    def _run(agent_a: Any, agent_b: Any) -> _SimResult:
        # Exercise our agent so latency/fallback telemetry is populated.
        for _ in range(5):
            agent_a({"player": 0, "step": 0}, None)
        return _SimResult(
            our_coins=coins,
            opp_coins=opp,
            trajectory=[3000.0, coins],
            completed=True,
            status="DONE",
        )

    return _run


def test_metrics_agent_records_latency_and_fallback() -> None:
    calls = {"n": 0}

    def flaky(obs: dict[str, Any], configuration: Any = None) -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] % 2 == 0:
            raise RuntimeError("boom")
        return {"farmer": ["PASS"], "hands": [], "market": []}

    m = MetricsAgent(flaky)
    for _ in range(4):
        m({"player": 0}, None)
    assert m.calls == 4
    assert m.fallbacks == 2
    assert len(m.latencies) == 4


def test_run_match_with_injected_simulator() -> None:
    champ: dict[str, Any] = {"farmer": ["PASS"], "hands": [], "market": []}

    def agent(obs: dict[str, Any], configuration: Any = None) -> dict[str, Any]:
        return dict(champ)

    runner = BenchmarkRunner(
        our_agent=agent,
        opponents={"starter": "starter"},
        seeds=(0, 1),
        candidate_name="test",
        simulator=_fake_simulator(21000.0, 3200.0),
    )
    matches = runner.run()
    assert len(matches) == 2
    m = matches[0]
    assert m.our_final_coins == 21000.0
    assert m.opponent_final_coins == 3200.0
    assert m.winner == 0
    assert m.fallback_count == 0
    assert m.episode_completed is True
    assert m.avg_decision_ms >= 0.0
    assert m.p95_decision_ms >= 0.0


def test_winner_from_rewards() -> None:
    assert winner_from_rewards(100, 50) == 0
    assert winner_from_rewards(50, 100) == 1
    assert winner_from_rewards(100, 100) == -1


def test_opponent_summary_aggregates() -> None:
    s = OpponentSummary(opponent="x")
    s.games = 4
    s.wins = 3
    s.losses = 1
    assert s.win_rate == 0.75
    lo, hi = s.win_rate_ci95()
    assert lo < 0.75 < hi


def test_benchmark_summary_metrics() -> None:
    matches = [
        MatchMetrics(
            episode_id="a",
            seed=0,
            our_agent="c",
            opponent="o",
            our_final_coins=20000.0,
            opponent_final_coins=3000.0,
            winner=0,
            coin_margin=17000.0,
            turns_completed=720,
            runtime_ms=1.0,
            avg_decision_ms=1.0,
            p95_decision_ms=2.0,
            max_decision_ms=3.0,
            fallback_count=0,
            invalid_actions=0,
            episode_completed=True,
            errors=0,
        ),
        MatchMetrics(
            episode_id="b",
            seed=1,
            our_agent="c",
            opponent="o",
            our_final_coins=18000.0,
            opponent_final_coins=3000.0,
            winner=0,
            coin_margin=15000.0,
            turns_completed=720,
            runtime_ms=1.0,
            avg_decision_ms=1.0,
            p95_decision_ms=2.0,
            max_decision_ms=3.0,
            fallback_count=0,
            invalid_actions=0,
            episode_completed=True,
            errors=0,
        ),
    ]
    s = BenchmarkSummary(candidate="c", matches=matches)
    assert s.total_wins() == 2
    assert s.overall_win_rate() == 1.0
    assert s.avg_coins() == 19000.0
    assert s.median_coins() == 19000.0
    assert s.by_opponent()["o"].games == 2
