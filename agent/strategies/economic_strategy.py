"""Stage 2 — Economic Strategy.

An adaptive economic strategy that evaluates actions based on expected
profitability, market conditions, opportunity costs, and multi-turn plans.
Falls back to Stage 1 baseline behavior on any error.
"""
from __future__ import annotations

from typing import Any

from agent.decision.candidate_actions import CandidateAction
from agent.decision.decision_context import DecisionContext
from agent.strategies.strategy import ScoredAction, Strategy
from agent.economics.economic_state import EconomicEvaluator, EconomicState
from agent.economics.profit_model import ProfitabilityEstimate
from agent.market.market_intelligence import MarketIntelligenceEngine
from agent.optimization.crop_optimizer import CropOptimizer, CropRecommendation
from agent.optimization.animal_optimizer import AnimalOptimizer
from agent.optimization.land_optimizer import LandOptimizer
from agent.optimization.worker_optimizer import WorkerOptimizer
from agent.optimization.resource_optimizer import ResourceOptimizer
from agent.planning.planner import Planner, PlannerConfig
from agent.strategies.baseline_strategy import BaselineStrategy
from agent.strategies.scoring import score_action
from agent.strategies.strategy import ScoredAction, Strategy
from agent.strategies.priorities import get_priority


class EconomicStrategy(Strategy):
    """Strategy that uses economic reasoning to rank actions.

    Integrates:
    - Economic state evaluation (net worth, profit, opportunity cost)
    - Market intelligence (price tracking, forecasting, demand)
    - Multi-turn planning (lookahead, rollout)
    - Optimization (crops, animals, workers, land)
    - Risk awareness

    Falls back to BaselineStrategy on any internal error.
    """

    def __init__(self) -> None:
        self._baseline = BaselineStrategy()
        self._economic = EconomicEvaluator()
        self._market_intel = MarketIntelligenceEngine()
        self._crop_opt = CropOptimizer()
        self._animal_opt = AnimalOptimizer()
        self._land_opt = LandOptimizer()
        self._worker_opt = WorkerOptimizer()
        self._resource_opt = ResourceOptimizer()
        self._planner = Planner(config={
            "horizon_turns": 5,
            "max_rollouts": 10,
            "max_branching": 8,
            "enable_planning": True,
        })

    def evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        """Evaluate actions using economic reasoning."""
        try:
            return self._economic_evaluate(context, actions)
        except Exception:
            return self._baseline.evaluate(context, actions)

    def _economic_evaluate(
        self,
        context: DecisionContext,
        actions: list[CandidateAction],
    ) -> list[ScoredAction]:
        game_state = context.game_state
        if game_state is None:
            return self._baseline.evaluate(context, actions)

        self._update_market_intelligence(context)

        econ_state = self._economic.evaluate(game_state)

        scored: list[ScoredAction] = []
        for action in actions:
            baseline_score, baseline_explanation = score_action(action)
            economic_bonus = self._economic_bonus(action, context, econ_state)
            market_bonus = self._market_bonus(action, context)
            plan_bonus = self._planning_bonus(action, context, econ_state)
            risk_penalty = self._risk_penalty(action, econ_state)

            total_score = (
                baseline_score
                + economic_bonus
                + market_bonus
                + plan_bonus
                - risk_penalty
            )

            explanation = (
                f"baseline={baseline_score:.2f}, "
                f"econ_bonus={economic_bonus:.2f}, "
                f"market_bonus={market_bonus:.2f}, "
                f"plan_bonus={plan_bonus:.2f}, "
                f"risk_penalty={risk_penalty:.2f}"
            )
            scored.append(ScoredAction(action, total_score, explanation))

        scored.sort(key=lambda s: (-s.score, get_priority(s.action.action_type), s.action.id))
        return scored

    def _update_market_intelligence(self, context: DecisionContext) -> None:
        obs = context.obs
        if not obs or "market" not in obs:
            return
        market = obs.get("market", {})
        turn = context.step or 0
        self._market_intel.update(
            turn=turn,
            prices=market.get("prices", {}),
            inventory=market.get("inventory", {}),
        )

    def _economic_bonus(
        self,
        action: CandidateAction,
        context: DecisionContext,
        econ_state: EconomicState,
    ) -> float:
        action_type = action.action_type
        bonus = 0.0

        if action_type in ("plant", "buy_seed"):
            current_day = context.day
            remaining_turns = context.remaining_turns
            market_prices = self._get_market_prices(context)
            seeds = context.game_state.private.get("seeds", {}) if context.game_state else {}

            best_crop: CropRecommendation | None = None
            try:
                best_crop = self._crop_opt.optimal_crop(
                    current_day=current_day,
                    remaining_turns=remaining_turns,
                    market_prices=market_prices,
                    available_seeds=seeds,
                    available_cash=econ_state.cash,
                    planted_tiles={},
                )
            except Exception:
                pass

            if best_crop is not None:
                bonus += best_crop.score * 0.1

        if action_type in ("sell",):
            bonus += 5.0

        if action_type in ("buy_land",):
            farm_profit = econ_state.expected_profit
            tiles = 25
            land_rec = self._land_opt.evaluate_expansion(
                available_cash=econ_state.cash,
                unlocked_quadrants=econ_state.unlocked_quadrants,
                remaining_turns=econ_state.remaining_turns,
                farm_profit_per_turn=farm_profit,
                tile_count=tiles,
            )
            if land_rec:
                bonus += land_rec[0].roi * 0.05

        return bonus

    def _market_bonus(self, action: CandidateAction, context: DecisionContext) -> float:
        action_type = action.action_type
        bonus = 0.0

        if action_type in ("sell",):
            market = context.game_state.market if context.game_state else None
            if market and hasattr(market, "prices"):
                prices = market.prices
                shed = context.game_state.private.get("shed", {}) if context.game_state else {}
                for item in shed:
                    intel = self._market_intel.get_intelligence(
                        item, prices.get(item, 1), shed.get(item, 0)
                    )
                    if intel.is_sell_opportunity:
                        bonus += 10.0
                    else:
                        bonus += 1.0

        if action_type in ("buy_seed", "buy_animal", "buy_product"):
            bonus += 2.0

        return bonus

    def _planning_bonus(
        self,
        action: CandidateAction,
        context: DecisionContext,
        econ_state: EconomicState,
    ) -> float:
        action_type = action.action_type
        bonus = 0.0

        if action_type in ("plant",):
            bonus += 8.0
        if action_type in ("buy_land",):
            bonus += 5.0
        if action_type in ("build_coop", "build_pasture"):
            bonus += 3.0
        if action_type in ("buy_animal",):
            bonus += 2.0

        if econ_state.remaining_turns < 100 and action_type in ("harvest", "sell"):
            bonus += 15.0

        return bonus

    def _risk_penalty(
        self,
        action: CandidateAction,
        econ_state: EconomicState,
    ) -> float:
        penalty = 0.0
        action_type = action.action_type

        if action.estimated_cost > econ_state.available_capital:
            penalty += 50.0

        if econ_state.remaining_turns < 50 and action_type in ("plant", "buy_animal", "buy_land"):
            payback = getattr(action, "estimated_cost", 0) / max(1, getattr(action, "estimated_reward", 1))
            if payback > econ_state.remaining_turns:
                penalty += 20.0

        return penalty

    def _get_market_prices(self, context: DecisionContext) -> dict[str, int]:
        market = context.game_state.market if context.game_state else None
        if market and hasattr(market, "prices"):
            return dict(market.prices)
        obs = context.obs
        if "market" in obs:
            return obs.get("market", {}).get("prices", {})
        return {}