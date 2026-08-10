"""Stage 2 — Opponent intelligence.

Models legally observable opponent state (wealth, expansion, production) using
only information exposed by the official observation. Never accesses hidden
state and never uses future information.
"""

from __future__ import annotations

from typing import Any


class OpponentModel:
    """Tracks observable opponent state over the episode.

    Each :meth:`update` call records a snapshot of what is legitimately
    visible at a given turn. Estimates (wealth, growth, threat) are derived
    exclusively from these snapshots.
    """

    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []
        self._max_snapshots = 200

    def update(
        self,
        turn: int,
        money: float | None = None,
        unlocked_tiles: int | None = None,
        active_tiles: int | None = None,
        market_activity: dict[str, int] | None = None,
    ) -> None:
        """Record one observable snapshot of the opponent at ``turn``."""
        self._snapshots.append(
            {
                "turn": turn,
                "money": money,
                "unlocked_tiles": unlocked_tiles,
                "active_tiles": active_tiles,
                "market_activity": dict(market_activity or {}),
            }
        )
        if len(self._snapshots) > self._max_snapshots:
            self._snapshots = self._snapshots[-self._max_snapshots :]

    @property
    def latest(self) -> dict[str, Any] | None:
        return self._snapshots[-1] if self._snapshots else None

    @property
    def snapshot_count(self) -> int:
        return len(self._snapshots)

    def estimate_money(self) -> float | None:
        snapshot = self.latest
        return snapshot["money"] if snapshot else None

    def estimate_wealth_growth(self, window: int = 5) -> float | None:
        if len(self._snapshots) < 2:
            return None
        recent = self._snapshots[-max(2, window) :]
        with_money = [s["money"] for s in recent if s["money"] is not None]
        if len(with_money) < 2:
            return None
        return float(with_money[-1] - with_money[0])

    def threat_level(self, my_money: float) -> float:
        """Estimate how large a threat the opponent represents (0..1)."""
        money = self.estimate_money()
        if money is None:
            return 0.5
        ratio = money / max(1.0, my_money)
        if ratio > 1.5:
            return 0.9
        if ratio > 1.1:
            return 0.7
        if ratio > 0.9:
            return 0.5
        return 0.3

    def reset(self) -> None:
        self._snapshots.clear()


class CompetitiveDecisionMaker:
    """Makes competitive decisions based on opponent intelligence."""

    def __init__(self) -> None:
        self._opponent_model: OpponentModel | None = None
        self._risk_aversion = 0.0

    def set_opponent_model(self, model: OpponentModel) -> None:
        self._opponent_model = model

    def make_decision(
        self,
        my_state: Any,
        opponent_state: Any,
        context: Any,
    ) -> dict[str, Any]:
        if self._opponent_model is None:
            return self._absolute_optimization(my_state, context)

        if self._should_avoid_risk(my_state, opponent_state):
            return self._defensive_strategy(my_state, context)

        if self._is_leading(my_state, opponent_state):
            return self._profit_optimization(my_state, context)

        return self._balanced_strategy(my_state, context)

    def _should_avoid_risk(
        self,
        my_state: Any,
        opponent_state: Any,
    ) -> bool:
        return getattr(my_state, "remaining_turns", 720) < 50

    def _defensive_strategy(
        self,
        my_state: Any,
        context: Any,
    ) -> dict[str, Any]:
        return {
            "action": "cash_preservation",
            "strategy": "defensive",
            "risk_level": "high",
            "expected_value": getattr(my_state, "cash", 0),
        }

    def _is_leading(
        self,
        my_state: Any,
        opponent_state: Any,
    ) -> bool:
        return getattr(my_state, "money", 0) > getattr(opponent_state, "money", 0) * 1.5

    def _profit_optimization(
        self,
        my_state: Any,
        context: Any,
    ) -> dict:
        return {
            "action": "aggressive_production",
            "strategy": "profit",
            "risk_level": "medium",
            "expected_value": getattr(my_state, "money", 0) * 1.1,
        }

    def _balanced_strategy(
        self,
        my_state: Any,
        context: Any,
    ) -> dict:
        return {
            "action": "balanced",
            "strategy": "balanced",
            "risk_level": "medium",
            "expected_value": getattr(my_state, "money", 0) * 1.05,
        }

    def _absolute_optimization(
        self,
        my_state: Any,
        context: Any,
    ) -> dict:
        return {
            "action": "absolute",
            "strategy": "absolute_optimization",
            "risk_level": "low",
            "expected_value": getattr(my_state, "cash", 0),
        }
