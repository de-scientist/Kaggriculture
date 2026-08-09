from __future__ import annotations

from typing import Any

from agent.competition.opponent_model import OpponentModel


class CompetitiveDecisionMaker:
    """Makes competitive decisions based on opponent intelligence."""

    def __init__(self):
        self._opponent_model: OpponentModel | None = None
        self._risk_aversion = 0.0

    def set_opponent_model(self, model: OpponentModel) -> None:
        self._opponent_model = model

    def make_decision(
        self,
        my_state: Any,
        opponent_state: Any,
        context: Any,
    ) -> dict:
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
        return my_state.remaining_turns < 50

    def _defensive_strategy(
        self,
        my_state: Any,
        context: Any,
    ) -> dict:
        return {
            "action": "cash_preservation",
            "strategy": "defensive",
            "risk_level": "high",
            "expected_value": my_state.cash,
        }

    def _is_leading(
        self,
        my_state: Any,
        opponent_state: Any,
    ) -> bool:
        return my_state.money > opponent_state.money * 1.5

    def _profit_optimization(
        self,
        my_state: Any,
        context: Any,
    ) -> dict:
        return {
            "action": "aggressive_production",
            "strategy": "profit",
            "risk_level": "medium",
            "expected_value": my_state.money * 1.1,
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
            "expected_value": my_state.money * 1.05,
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
            "expected_value": my_state.cash,
        }