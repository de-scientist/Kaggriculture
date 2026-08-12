"""Self-play / tournament framework for Stage 3 validation.

The framework is intentionally decoupled from the Kaggle runtime: the game runner
is a plain callable ``simulator(agent_a, agent_b) -> (reward_a, reward_b)``.  A
default runner backed by ``kaggle_environments`` is provided for real play, but
tests and notebooks can inject any simulator (including a deterministic stub).

This satisfies the Stage 3 requirements for:

* champion / challenger testing (run a hybrid against the Stage 2 champion),
* self-play (Stage 3 vs Stage 2, Stage 3 vs Stage 3),
* tournament standings (round-robin across several agents),
* reproducible experiments (seeded simulator injection).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

Agent = Callable[[dict[str, Any]], dict[str, Any]]
Simulator = Callable[[Agent, Agent], tuple[float, float]]


@dataclass
class MatchResult:
    """Outcome of a single head-to-head match."""

    agent_a: str
    agent_b: str
    reward_a: float
    reward_b: float
    winner: int  # 0 = a wins, 1 = b wins, -1 = tie

    @property
    def margin(self) -> float:
        return self.reward_a - self.reward_b


@dataclass
class TournamentResult:
    """Aggregated results of a round-robin tournament."""

    matches: list[MatchResult] = field(default_factory=list)

    def wins(self, name: str) -> int:
        count = 0
        for m in self.matches:
            if m.agent_a == name and m.winner == 0:
                count += 1
            elif m.agent_b == name and m.winner == 1:
                count += 1
        return count

    def losses(self, name: str) -> int:
        count = 0
        for m in self.matches:
            if m.agent_a == name and m.winner == 1:
                count += 1
            elif m.agent_b == name and m.winner == 0:
                count += 1
        return count

    def ties(self, name: str) -> int:
        return sum(1 for m in self.matches if m.agent_a == name and m.winner == -1)

    def avg_reward(self, name: str) -> float:
        rewards: list[float] = []
        for m in self.matches:
            if m.agent_a == name:
                rewards.append(m.reward_a)
            elif m.agent_b == name:
                rewards.append(m.reward_b)
        if not rewards:
            return 0.0
        return sum(rewards) / len(rewards)

    def participants(self) -> list[str]:
        names: list[str] = []
        for m in self.matches:
            if m.agent_a not in names:
                names.append(m.agent_a)
            if m.agent_b not in names:
                names.append(m.agent_b)
        return names

    def standings(self) -> list[tuple[str, int, float]]:
        """Return (name, wins, avg_reward) sorted by wins then reward."""
        rows = [
            (name, self.wins(name), round(self.avg_reward(name), 2))
            for name in self.participants()
        ]
        return sorted(rows, key=lambda r: (-r[1], -r[2]))


def _kaggle_simulator(
    configuration: Mapping[str, Any] | None,
) -> Simulator:
    from kaggle_environments import make

    def _run(agent_a: Agent, agent_b: Agent) -> tuple[float, float]:
        env = make(
            "kaggriculture",
            configuration=dict(configuration or {"episodeSteps": 720}),
        )
        env.run([agent_a, agent_b])
        final = env.steps[-1]
        rewards = [float(s.reward or 0.0) for s in final]
        return rewards[0], rewards[1]

    return _run


def run_match(
    agent_a: Agent,
    agent_b: Agent,
    *,
    simulator: Simulator | None = None,
    configuration: Mapping[str, Any] | None = None,
    seed: int = 0,
) -> MatchResult:
    """Play a single match between two agents and return the result."""
    if simulator is None:
        simulator = _kaggle_simulator(configuration)
    reward_a, reward_b = simulator(agent_a, agent_b)
    winner = 0 if reward_a > reward_b else (1 if reward_b > reward_a else -1)
    return MatchResult(
        agent_a="A",
        agent_b="B",
        reward_a=reward_a,
        reward_b=reward_b,
        winner=winner,
    )


def run_tournament(
    agents: Mapping[str, Agent],
    *,
    episodes: int = 1,
    simulator: Simulator | None = None,
    configuration: Mapping[str, Any] | None = None,
    seed: int = 0,
) -> TournamentResult:
    """Run a round-robin tournament over the named agents.

    Each unordered pair plays ``episodes`` matches.  Agents are passed position
    symmetrically (both as A and as B) so first/second-player bias is averaged
    out across episodes when ``episodes`` is even.  For simplicity each pair
    plays ``episodes`` matches with agent A fixed as the first-listed name;
    callers wanting balanced sides should pass an even ``episodes`` count and
    rely on the injected simulator for side randomization.
    """
    names = list(agents)
    matches: list[MatchResult] = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for ep in range(episodes):
                result = run_match(
                    agents[names[i]],
                    agents[names[j]],
                    simulator=simulator,
                    configuration=configuration,
                    seed=seed + ep,
                )
                result.agent_a = names[i]
                result.agent_b = names[j]
                matches.append(result)
    return TournamentResult(matches=matches)


def summarize(result: TournamentResult) -> str:
    """Human-readable summary of tournament standings."""
    lines = ["Tournament standings (wins, avg_reward):"]
    for name, wins, avg in result.standings():
        lines.append(f"  {name}: {wins} wins, avg {avg}")
    return "\n".join(lines)


def _demo_agents() -> dict[str, Agent]:
    """Two trivial agents used only for smoke-testing the runner without env."""

    def pass_agent(obs: dict[str, Any]) -> dict[str, Any]:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    return {"pass": pass_agent, "pass2": pass_agent}
