"""Benchmark runner for Stage 4B competitive validation.

Runs 720-turn matches between a candidate agent (always player 0, instrumented
for latency/fallback telemetry) and a suite of opponents, collecting rich
:class:`~agent.evaluation.metrics.MatchMetrics`.  The game runner is injected so
the runner is testable without the Kaggle runtime; a default runner backed by
``kaggle_environments`` is provided for real play.

Reuses :mod:`agent.submission.failsafe` (two-argument Kaggle convention) and the
opponent presets in :mod:`agent.evaluation.opponents`.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from agent.evaluation.metrics import (
    BenchmarkSummary,
    MatchMetrics,
    percentile,
    winner_from_rewards,
)
from agent.submission.failsafe import EMERGENCY_ACTION, FailSafeAgent

Agent = Any


@dataclass
class _SimResult:
    our_coins: float
    opp_coins: float
    trajectory: list[float]
    completed: bool
    status: str


class MetricsAgent:
    """Wrap an agent to record per-call latency and fallbacks.

    Tolerates the Kaggle two-argument call and never raises (it returns the
    emergency action on failure so telemetry still captures the fallback).
    """

    def __init__(self, agent_fn: Agent) -> None:
        self._agent = agent_fn
        self.calls = 0
        self.total_ms = 0.0
        self.max_ms = 0.0
        self.latencies: list[float] = []
        self.fallbacks = 0

    def __call__(self, obs: Mapping[str, Any], configuration: Any = None) -> dict[str, Any]:
        started = time.perf_counter()
        try:
            out = self._agent(obs, configuration)
        except Exception:  # noqa: BLE001 - capture fallback, never propagate
            out = dict(EMERGENCY_ACTION)
        dt = (time.perf_counter() - started) * 1000.0
        self.calls += 1
        self.total_ms += dt
        self.max_ms = max(self.max_ms, dt)
        self.latencies.append(dt)
        if out == EMERGENCY_ACTION:
            self.fallbacks += 1
        return cast("dict[str, Any]", out)


def _kaggle_simulator(configuration: Mapping[str, Any] | None) -> Callable[..., _SimResult]:
    from kaggle_environments import make

    def _run(our_agent: Agent, opponent: Agent) -> _SimResult:
        env = make("kaggriculture", configuration=dict(configuration or {"episodeSteps": 720}))
        env.run([our_agent, opponent])
        final = env.steps[-1]
        our = final[0]
        opp = final[1]
        our_coins = float(our.reward if our.reward is not None else our.observation["farms"][0]["money"])
        opp_coins = float(opp.reward if opp.reward is not None else opp.observation["farms"][0]["money"])
        trajectory: list[float] = []
        for step in env.steps:
            try:
                trajectory.append(float(step[0].observation["farms"][0]["money"]))
            except Exception:  # noqa: BLE001
                break
        status = str(getattr(our, "status", "DONE") or "DONE")
        return _SimResult(
            our_coins=our_coins,
            opp_coins=opp_coins,
            trajectory=trajectory,
            completed=status == "DONE",
            status=status,
        )

    return _run


@dataclass
class BenchmarkRunner:
    """Run candidate-vs-opponent matches and collect metrics."""

    our_agent: Agent
    opponents: Mapping[str, Agent] = field(default_factory=dict)
    seeds: Sequence[int] = (0, 1, 2)
    configuration: Mapping[str, Any] = field(default_factory=lambda: {"episodeSteps": 720})
    simulator: Callable[..., _SimResult] | None = None
    candidate_name: str = "champion"

    def _sim(self) -> Callable[..., _SimResult]:
        return self.simulator if self.simulator is not None else _kaggle_simulator(self.configuration)

    def run_match(self, opponent_name: str, opponent: Agent, seed: int) -> MatchMetrics:
        if isinstance(self.our_agent, FailSafeAgent):
            fs_agent = self.our_agent
        else:
            fs_agent = FailSafeAgent(self.our_agent, stats={})
        instrumented = MetricsAgent(fs_agent)
        started = time.perf_counter()
        result = self._sim()(instrumented, opponent)
        runtime_ms = (time.perf_counter() - started) * 1000.0
        winner = winner_from_rewards(result.our_coins, result.opp_coins)
        avg = (instrumented.total_ms / instrumented.calls) if instrumented.calls else 0.0
        return MatchMetrics(
            episode_id=f"{self.candidate_name}-vs-{opponent_name}-s{seed}",
            seed=seed,
            our_agent=self.candidate_name,
            opponent=opponent_name,
            our_final_coins=result.our_coins,
            opponent_final_coins=result.opp_coins,
            winner=winner,
            coin_margin=result.our_coins - result.opp_coins,
            turns_completed=len(result.trajectory),
            runtime_ms=runtime_ms,
            avg_decision_ms=avg,
            p95_decision_ms=percentile(instrumented.latencies, 95.0),
            max_decision_ms=instrumented.max_ms,
            fallback_count=fs_agent._stats.get("fallback", 0),
            invalid_actions=0,
            episode_completed=result.completed,
            errors=1 if result.status == "ERROR" else 0,
            trajectory=result.trajectory,
        )

    def run(self, opponents: Mapping[str, Agent] | None = None) -> list[MatchMetrics]:
        opps = opponents if opponents is not None else self.opponents
        matches: list[MatchMetrics] = []
        for name, agent in opps.items():
            for seed in self.seeds:
                matches.append(self.run_match(name, agent, seed))
        return matches

    def summarize(self, matches: Sequence[MatchMetrics]) -> BenchmarkSummary:
        return BenchmarkSummary(candidate=self.candidate_name, matches=list(matches))
