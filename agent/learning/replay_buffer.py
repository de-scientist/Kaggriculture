"""Bounded, prioritized replay buffer for experience curation.

The buffer holds experience rows grouped by episode with a bounded total
capacity.  Priorities let downstream training focus on high-signal rows
(high prediction error, big wealth swings, endgame turns, close games, rare
opponents).  Everything is deterministic under a fixed seed.
"""

from __future__ import annotations

import json
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass
class ReplayRow:
    """One experience row with a computed priority."""

    data: dict[str, Any]
    priority: float = 0.0
    episode_id: str = ""
    step: int = 0

    def __post_init__(self) -> None:
        if not self.episode_id:
            self.episode_id = str(self.data.get("episode_id", ""))
        if not self.step:
            try:
                self.step = int(self.data.get("step", 0))
            except (TypeError, ValueError):
                self.step = 0


class PrioritizedReplayBuffer:
    """Bounded buffer with priority-weighted sampling and episode grouping."""

    def __init__(
        self,
        capacity: int = 100_000,
        seed: int = 0,
        priority_fn: Callable[[dict[str, Any]], float] | None = None,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.seed = seed
        self._rng = random.Random(seed)
        self._priority_fn = priority_fn or _default_priority
        self._rows: list[ReplayRow] = []

    # -- storage ----------------------------------------------------------
    def add(self, data: Mapping[str, Any]) -> None:
        row = ReplayRow(dict(data))
        if self._priority_fn is not None:
            try:
                row.priority = float(self._priority_fn(row.data))
            except (TypeError, ValueError):
                row.priority = 0.0
        self._rows.append(row)
        if len(self._rows) > self.capacity:
            self._rows.sort(key=lambda r: r.priority)
            del self._rows[: len(self._rows) - self.capacity]

    def add_many(self, rows: Iterable[Mapping[str, Any]]) -> None:
        for row in rows:
            self.add(row)

    def clear(self) -> None:
        self._rows.clear()

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def rows(self) -> list[ReplayRow]:
        return list(self._rows)

    # -- queries ----------------------------------------------------------
    def episode_ids(self) -> set[str]:
        return {r.episode_id for r in self._rows if r.episode_id}

    def by_episode(self, episode_id: str) -> list[ReplayRow]:
        return [r for r in self._rows if r.episode_id == episode_id]

    def episodes(self) -> list[list[ReplayRow]]:
        groups: dict[str, list[ReplayRow]] = {}
        for row in self._rows:
            groups.setdefault(row.episode_id, []).append(row)
        return [rows for rows in groups.values() if rows]

    def sample(self, n: int, replace: bool = False, weighted: bool = True) -> list[ReplayRow]:
        """Sample rows, optionally weighted by priority."""
        if n <= 0 or not self._rows:
            return []
        n = min(n, len(self._rows)) if not replace else n
        if weighted and sum(r.priority for r in self._rows) > 0:
            weights = [r.priority for r in self._rows]
            return self._rng.choices(self._rows, weights=weights, k=n)
        return [self._rows[i] for i in self._rng.sample(range(len(self._rows)), n)]

    def filter(self, predicate: Callable[[dict[str, Any]], bool]) -> PrioritizedReplayBuffer:
        kept = [r.data for r in self._rows if predicate(r.data)]
        out = PrioritizedReplayBuffer(
            capacity=self.capacity, seed=self.seed, priority_fn=self._priority_fn
        )
        out.add_many(kept)
        return out

    def stats(self) -> dict[str, Any]:
        priorities = [r.priority for r in self._rows]
        return {
            "n_rows": len(self._rows),
            "n_episodes": len(self.episode_ids()),
            "priority_min": min(priorities) if priorities else 0.0,
            "priority_max": max(priorities) if priorities else 0.0,
            "priority_mean": (sum(priorities) / len(priorities)) if priorities else 0.0,
        }

    # -- persistence ------------------------------------------------------
    def to_json(self) -> str:
        return json.dumps(
            {
                "capacity": self.capacity,
                "seed": self.seed,
                "rows": [r.data for r in self._rows],
            },
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, raw: str) -> PrioritizedReplayBuffer:
        payload = json.loads(raw)
        buffer = cls(
            capacity=int(payload.get("capacity", 100_000)), seed=int(payload.get("seed", 0))
        )
        buffer.add_many(payload.get("rows", []))
        return buffer


def _default_priority(data: Mapping[str, Any]) -> float:
    """Heuristic priority emphasizing high-signal experiences.

    High-priority rows: large absolute wealth moves between consecutive turns
    (proxy for harvests, sales, big investments), late-game rows, close games.
    """
    score = 1.0
    raw_state = data.get("state")
    state: Mapping[str, Any] = raw_state if isinstance(raw_state, Mapping) else {}
    money = state.get("money", 0.0)
    try:
        money = float(money)
    except (TypeError, ValueError):
        money = 0.0
    delta = data.get("money_delta", 0.0)
    try:
        delta = float(delta)
    except (TypeError, ValueError):
        delta = 0.0
    if abs(delta) >= 500.0:
        score += 3.0
    elif abs(delta) >= 100.0:
        score += 1.5
    day = 0
    try:
        day = int(data.get("day", 0))
    except (TypeError, ValueError):
        day = 0
    if day >= 25:
        score += 1.0
    if data.get("outcome_money") is not None:
        try:
            if float(data["outcome_money"]) < 8000.0:
                score += 1.0
        except (TypeError, ValueError):
            pass
    return score
