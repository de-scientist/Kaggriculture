"""Stage 2 — Competitive strategy.

Adjusts action rankings based on observable opponent state. When leading,
low-risk actions are favored; when trailing, higher-upside production actions
are favored. Always falls back to the Stage 1 baseline on any error.
"""

from __future__ import annotations

from agent.competition.opponent_model import OpponentModel
from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.priorities import get_priority
from agent.strategies.strategy import ScoredAction, Strategy


class CompetitiveStrategy(Strategy):
    """Strategy that factors observable opponent state into action ranking."""

    def __init__(self) -> None:
        self._baseline = BaselineStrategy()
        self._opponent_model = OpponentModel()

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        try:
            self._update_opponent_model(context)
            scored = self._baseline.evaluate(context, actions)
            adjusted = [self._adjust(sa, context) for sa in scored]
            adjusted.sort(key=lambda s: (-s.score, get_priority(s.action.action_type), s.action.id))
            return adjusted
        except Exception:
            return self._baseline.evaluate(context, actions)

    def _update_opponent_model(self, context: DecisionContext) -> None:
        game_state = getattr(context, "game_state", None)
        if game_state is None:
            return
        opponent = getattr(game_state, "opponent", None)
        opponent_money = getattr(opponent, "money", None) if opponent is not None else None
        unlocked_tiles = None
        if opponent is not None and getattr(opponent, "farm", None) is not None:
            unlocked_tiles = len(getattr(opponent.farm, "tiles", {}) or {})
        self._opponent_model.update(
            turn=getattr(context, "step", 0),
            money=opponent_money,
            unlocked_tiles=unlocked_tiles,
            active_tiles=unlocked_tiles,
        )

    def _adjust(self, scored: ScoredAction, context: DecisionContext) -> ScoredAction:
        game_state = getattr(context, "game_state", None)
        my_money = 0.0
        if game_state is not None:
            farm = getattr(game_state, "farm", None)
            if farm is not None:
                my_money = float(getattr(farm, "money", 0.0))
        threat = self._opponent_model.threat_level(my_money)
        action_type = scored.action.action_type
        bonus = 0.0
        if threat < 0.5 and action_type in ("buy_land", "buy_animal", "buy_product"):
            bonus = -2.0
        if threat > 0.7 and action_type in ("plant", "sell", "harvest"):
            bonus = 3.0
        scored.score += bonus
        scored.explanation = f"threat={threat:.2f}, {scored.explanation}"
        return scored
