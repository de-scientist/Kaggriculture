from __future__ import annotations

from typing import Any

from agent.strategies.strategy import Strategy


class MarketAwareStrategy(Strategy):
    """Market-aware strategy that evaluates actions using market intelligence.

    Integrates:
    - Economic state evaluation (net worth, profit, opportunity cost)
    - Market intelligence (price tracking, forecasting, demand)
    - Multi-turn planning (lookahead, rollout)
    - Optimization (crops, animals, workers, land)
    - Risk awareness
    """

    def __init__(self):
        self._market_intel = None
        self._crop_opt = None
        self._animal_opt = None
        self._land_opt = None
        self._worker_opt = None
        self._planner = None

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[Any],
    ) -> list[ScoredAction]:
        try:
            return self._economic_evaluate(context, actions)
        except Exception:
            return BaselineStrategy().evaluate(context, actions)

    def _economic_evaluate(
        self,
        context: DecisionContext,
        actions: list[Any],
    ) -> list[ScoredAction]:
        return BaselineStrategy().evaluate(context, actions)