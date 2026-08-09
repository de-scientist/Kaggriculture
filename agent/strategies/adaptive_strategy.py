from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StrategyMode:
    name: str
    description: str
    conditions: dict[str, Any]


class AdaptiveStrategyController:
    """Selects strategy mode based on current economic state."""

    def __init__(self):
        self.modes: dict[str, StrategyMode] = {}
        self._current_mode: str = "growth"
        self._min_cash_threshold = 500.0
        self._min_profit_threshold = 0.0
        self._endgame_turns = 50
        self._expansion_threshold = 1.0

    def set_mode(self, mode: str) -> None:
        self._current_mode = mode

    def evaluate_mode(
        self,
        economic_state: Any,
        remaining_turns: int,
    ) -> StrategyMode:
        mode = self._current_mode
        conditions = self.modes.get(mode, {})

        if remaining_turns < self._endgame_turns:
            mode = "endgame"
        elif economic_state.expected_profit > self._min_profit_threshold:
            mode = "expansion" if economic_state.expected_revenue > 1000 else "production"
        elif economic_state.cash < self._min_cash_threshold:
            mode = "cash_preservation"
        elif economic_state.market_conditions == "bullish":
            mode = "market_exploitation"
        elif economic_state.remaining_turns < 100:
            mode = "growth"
        else:
            mode = "production"

        return StrategyMode(
            name=mode,
            description=f"Mode: {mode}",
            conditions=conditions,
        )

    def transition(
        self,
        current_mode: str,
        new_state: Any,
    ) -> str:
        new_mode = self._get_mode_from_state(new_state)
        return new_mode if new_mode else current_mode

    def _get_mode_from_state(
        self,
        state: Any,
    ) -> str | None:
        if state.expected_profit > 1000:
            return "expansion"
        if state.remaining_turns < 100:
            return "endgame"
        if state.cash < 500:
            return "cash_preservation"
        if state.market_conditions == "bullish":
            return "market_exploitation"
        return None