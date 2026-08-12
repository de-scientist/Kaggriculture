"""Match and benchmark metrics for Stage 4B competitive validation.

Collects per-match evidence (final coins, win/loss/tie, latency, fallbacks,
wealth trajectory) and aggregates it into opponent-level statistics with a
simple Wald confidence interval for the win rate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any


@dataclass
class MatchMetrics:
    """One head-to-head match from the perspective of ``our_agent`` (player 0)."""

    episode_id: str
    seed: int
    our_agent: str
    opponent: str
    our_final_coins: float
    opponent_final_coins: float
    winner: int  # 0 = our win, 1 = opponent win, -1 = tie
    coin_margin: float
    turns_completed: int
    runtime_ms: float
    avg_decision_ms: float
    p95_decision_ms: float
    max_decision_ms: float
    fallback_count: int
    invalid_actions: int
    episode_completed: bool
    errors: int
    trajectory: list[float] = field(default_factory=list)  # our money per step

    def to_dict(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "seed": self.seed,
            "our_agent": self.our_agent,
            "opponent": self.opponent,
            "our_final_coins": self.our_final_coins,
            "opponent_final_coins": self.opponent_final_coins,
            "winner": self.winner,
            "coin_margin": self.coin_margin,
            "turns_completed": self.turns_completed,
            "runtime_ms": self.runtime_ms,
            "avg_decision_ms": self.avg_decision_ms,
            "p95_decision_ms": self.p95_decision_ms,
            "max_decision_ms": self.max_decision_ms,
            "fallback_count": self.fallback_count,
            "invalid_actions": self.invalid_actions,
            "episode_completed": self.episode_completed,
            "errors": self.errors,
            "trajectory": self.trajectory,
        }


@dataclass
class OpponentSummary:
    """Aggregated statistics for ``our_agent`` against a single opponent."""

    opponent: str
    games: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0

    @property
    def win_rate(self) -> float:
        return self.wins / self.games if self.games else 0.0

    @property
    def loss_rate(self) -> float:
        return self.losses / self.games if self.games else 0.0

    @property
    def tie_rate(self) -> float:
        return self.ties / self.games if self.games else 0.0

    def win_rate_ci95(self) -> tuple[float, float]:
        """Wald 95% confidence interval for the win rate (clamped to [0, 1])."""
        if self.games == 0:
            return (0.0, 0.0)
        p = self.win_rate
        se = sqrt(p * (1.0 - p) / self.games)
        lo = max(0.0, p - 1.96 * se)
        hi = min(1.0, p + 1.96 * se)
        return (lo, hi)


@dataclass
class BenchmarkSummary:
    """Aggregated statistics across a set of matches for one candidate."""

    candidate: str
    matches: list[MatchMetrics] = field(default_factory=list)

    def by_opponent(self) -> dict[str, OpponentSummary]:
        out: dict[str, OpponentSummary] = {}
        for m in self.matches:
            s = out.setdefault(m.opponent, OpponentSummary(opponent=m.opponent))
            s.games += 1
            if m.winner == 0:
                s.wins += 1
            elif m.winner == 1:
                s.losses += 1
            else:
                s.ties += 1
        return out

    def total_wins(self) -> int:
        return sum(1 for m in self.matches if m.winner == 0)

    def total_losses(self) -> int:
        return sum(1 for m in self.matches if m.winner == 1)

    def total_ties(self) -> int:
        return sum(1 for m in self.matches if m.winner == -1)

    def avg_coins(self) -> float:
        return sum(m.our_final_coins for m in self.matches) / len(self.matches) if self.matches else 0.0

    def median_coins(self) -> float:
        if not self.matches:
            return 0.0
        vals = sorted(m.our_final_coins for m in self.matches)
        n = len(vals)
        mid = n // 2
        return float(vals[mid]) if n % 2 else float((vals[mid - 1] + vals[mid]) / 2)

    def best_coins(self) -> float:
        return max((m.our_final_coins for m in self.matches), default=0.0)

    def worst_coins(self) -> float:
        return min((m.our_final_coins for m in self.matches), default=0.0)

    def avg_margin(self) -> float:
        return sum(m.coin_margin for m in self.matches) / len(self.matches) if self.matches else 0.0

    def overall_win_rate(self) -> float:
        n = len(self.matches)
        return self.total_wins() / n if n else 0.0

    def avg_decision_ms(self) -> float:
        return sum(m.avg_decision_ms for m in self.matches) / len(self.matches) if self.matches else 0.0

    def max_decision_ms(self) -> float:
        return max((m.max_decision_ms for m in self.matches), default=0.0)

    def total_fallbacks(self) -> int:
        return sum(m.fallback_count for m in self.matches)


def winner_from_rewards(our_reward: float, opp_reward: float) -> int:
    if our_reward > opp_reward:
        return 0
    if opp_reward > our_reward:
        return 1
    return -1


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolated percentile (q in [0, 100]); returns 0.0 if empty."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return float(s[0])
    k = (len(s) - 1) * (q / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    frac = k - lo
    return float(s[lo] + (s[hi] - s[lo]) * frac)
