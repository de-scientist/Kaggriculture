"""Stage 3 — Safe exploration policy.

Implements bounded, safety-aware exploration for the learning layer.  Exploration
is never allowed to bypass legality: the caller is responsible for passing only
legal candidate options (already validated by the action generator / validator),
and this policy merely chooses *which* of those to try.  Exploration is:

* bounded by an absolute budget (``max_exploration_fraction`` of total turns),
* suppressed near the end of the episode (``min_remaining_turns``),
* suppressed when the learned policy is already confident, and
* suppressed when the remaining budget is exhausted.

Two selection modes are provided:

* :meth:`ExplorationPolicy.select` -- epsilon-greedy over scored options.
* :meth:`ExplorationPolicy.uncertainty_sample` -- pick the highest-uncertainty
  option to maximize information gain.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ExplorationConfig:
    """Tunable knobs for the exploration policy."""

    epsilon: float = 0.1
    max_exploration_fraction: float = 0.1
    min_remaining_turns: int = 50
    high_confidence_skip: float = 0.9
    seed: int = 0


class ExplorationPolicy(Generic[T]):
    """Bounded, safety-aware exploration over a set of legal options."""

    def __init__(self, config: ExplorationConfig | None = None) -> None:
        self.config = config or ExplorationConfig()
        self._rng = random.Random(self.config.seed)
        self._budget_left = 0
        self.total_turns = 0
        self.explored_count = 0

    def reset(self, total_turns: int) -> None:
        """Set the exploration budget for a new episode."""
        self.total_turns = total_turns
        self._budget_left = max(0, int(self.config.max_exploration_fraction * total_turns))
        self.explored_count = 0

    def remaining_budget(self) -> int:
        return self._budget_left

    def should_explore(
        self, *, remaining_turns: int, confidence: float, step: int
    ) -> bool:
        """Decide whether this turn is eligible for exploration."""
        if remaining_turns < self.config.min_remaining_turns:
            return False
        if confidence >= self.config.high_confidence_skip:
            return False
        if self._budget_left <= 0:
            return False
        if not 0.0 < self.config.epsilon <= 1.0:
            return False
        return self._rng.random() < self.config.epsilon

    def select(
        self,
        options: Sequence[T],
        scores: Sequence[float],
        *,
        remaining_turns: int,
        confidence: float,
        step: int,
    ) -> tuple[T, bool]:
        """Epsilon-greedy selection.

        Returns the chosen option and whether the choice was exploratory.
        """
        if not options:
            raise ValueError("exploration requires at least one option")
        if len(options) != len(scores):
            raise ValueError("options and scores must be the same length")
        if self.should_explore(
            remaining_turns=remaining_turns, confidence=confidence, step=step
        ):
            choice = self._rng.randrange(len(options))
            self._budget_left -= 1
            self.explored_count += 1
            return options[choice], True
        best = max(
            range(len(scores)),
            key=lambda i: scores[i] + self._rng.random() * 1e-9,
        )
        return options[best], False

    def uncertainty_sample(
        self, options: Sequence[T], uncertainties: Sequence[float]
    ) -> tuple[T, bool]:
        """Pick the highest-uncertainty option to maximize information gain."""
        if not options:
            raise ValueError("exploration requires at least one option")
        if len(options) != len(uncertainties):
            raise ValueError("options and uncertainties must be the same length")
        if self._budget_left <= 0:
            return options[0], False
        idx = max(range(len(uncertainties)), key=lambda i: uncertainties[i])
        self._budget_left -= 1
        self.explored_count += 1
        return options[idx], True
