"""Champion / challenger management for Stage 4.

Selecting the submission agent is a championship problem: candidates must be
compared under self-play with *champion protection* (a challenger only dethrones
the reigning champion when it wins by a clear margin, so noise cannot flip the
submission).  This module builds candidate agents from the production planner's
policy stack and runs them through the Stage 3 tournament framework.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ..evaluation.tournament import (
    Agent,
    Simulator,
    TournamentResult,
    run_tournament,
)
from ..runtime.agent import make_runtime_agent
from ..runtime.policies import Policy


@dataclass
class Candidate:
    """A named submission candidate backed by a policy or agent factory."""

    name: str
    description: str
    policy: str | Policy | None = "auto"
    tags: tuple[str, ...] = ()

    def build(self) -> Agent:
        policy = self.policy
        if isinstance(policy, str):
            return make_runtime_agent(policy)
        if isinstance(policy, Policy):
            return make_runtime_agent(policy)
        if policy is None:
            return make_runtime_agent(None)
        # A ready-made agent factory callable.
        return policy()


@dataclass
class ArenaConfig:
    episodes: int = 1
    win_margin: float = 0.0
    seed: int = 0
    configuration: Mapping[str, Any] | None = None
    simulator: Simulator | None = None


class ChampionArena:
    """Run a round-robin over candidates and select a protected champion."""

    def __init__(
        self,
        candidates: Sequence[Candidate],
        config: ArenaConfig | None = None,
    ) -> None:
        self.candidates = list(candidates)
        self.config = config or ArenaConfig()

    def build_agents(self) -> dict[str, Agent]:
        return {c.name: c.build() for c in self.candidates}

    def run(self) -> TournamentResult:
        return run_tournament(
            self.build_agents(),
            episodes=self.config.episodes,
            simulator=self.config.simulator,
            configuration=self.config.configuration,
            seed=self.config.seed,
        )

    def ranked(self, result: TournamentResult) -> list[tuple[str, int, float]]:
        return result.standings()

    def select_champion(
        self,
        result: TournamentResult,
        current_champion: str | None = None,
    ) -> str:
        """Pick the best candidate with champion protection.

        The incumbent wins ties; a challenger only takes the crown when it has
        strictly more wins, or equal wins and a strictly higher average reward
        by at least ``win_margin``.  Returns the champion name.
        """
        standings = self.ranked(result)
        if not standings:
            raise ValueError("no candidates participated in the arena")
        top_name, top_wins, top_avg = standings[0]
        if current_champion is None:
            return top_name
        champ_wins = result.wins(current_champion)
        champ_avg = result.avg_reward(current_champion)
        if top_name == current_champion:
            return current_champion
        # Challenger must clearly beat the incumbent.
        if top_wins > champ_wins:
            return top_name
        if top_wins == champ_wins and (top_avg - champ_avg) >= self.config.win_margin:
            return top_name
        return current_champion

    def report(self, result: TournamentResult, champion: str | None = None) -> str:
        lines = ["Champion arena standings (wins, avg_reward):"]
        for name, wins, avg in self.ranked(result):
            lines.append(f"  {name}: {wins} wins, avg {avg}")
        champ = champion or self.select_champion(result)
        lines.append(f"Selected champion: {champ}")
        return "\n".join(lines)


def default_candidates() -> list[Candidate]:
    """The candidate pool considered for the submission.

    All candidates share the production planner; they differ only in their
    policy wrapper.  The learned/hybrid candidates degrade to the champion
    automatically when no trained bundle is present, so they are always safe to
    include in the arena.
    """
    return [
        Candidate(
            name="champion_endgame",
            description="Championship hybrid: EndgamePolicy (wind-down + liquidation).",
            policy="auto",
            tags=("submission", "endgame"),
        ),
        Candidate(
            name="hybrid",
            description="Stage 3 HybridPolicy (bounded learned tie-breaker).",
            policy="hybrid",
            tags=("learned", "hybrid"),
        ),
        Candidate(
            name="learned",
            description="Stage 3 LearnedPolicy (value + policy signals).",
            policy="learned",
            tags=("learned"),
        ),
    ]


def select_champion_from_tournament(
    result: TournamentResult,
    candidates: Sequence[Candidate] | None = None,
    current_champion: str | None = None,
    config: ArenaConfig | None = None,
) -> str:
    """One-shot champion selection used by scripts and notebooks."""
    arena = ChampionArena(candidates or default_candidates(), config)
    return arena.select_champion(result, current_champion=current_champion)
