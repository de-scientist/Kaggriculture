"""Stage 2 — Multi-Turn Planner.

Performs lightweight lookahead planning to evaluate multi-turn action
sequences. Uses a greedy rollout approach with economic evaluation.
No future game-state information is used — only the current observable
state and documented game mechanics.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from agent.planning.plan import Plan, PlanStep, PlanEvaluation
from agent.economics.profit_model import (
    CROP_PARAMS,
    ANIMAL_PARAMS,
)


@dataclass
class PlannerConfig:
    """Configuration for the multi-turn planner."""

    horizon_turns: int = 5
    max_rollouts: int = 10
    max_branching: int = 8
    enable_planning: bool = True


@dataclass
class Planner:
    """Lightweight lookahead planner for multi-turn action evaluation.

    The planner generates candidate action sequences, simulates their
    economic outcomes, and returns a ranked list of plans.
    """

    config: PlannerConfig = field(default_factory=PlannerConfig)

    def plan(
        self,
        game_state: Any,
        current_turn: int,
        remaining_turns: int,
        available_cash: float,
    ) -> Plan:
        """Generate a plan for the current state.

        Uses greedy lookahaed with economic evaluation.
        Returns the best plan (may be a single-turn plan).
        """
        if not self.config.enable_planning or remaining_turns <= 0:
            return self._default_plan(current_turn)

        best_plan = self._default_plan(current_turn)

        # Evaluate immediate actions with lookahead
        candidates = self._generate_lookahead_candidates(
            game_state, current_turn, remaining_turns, available_cash
        )

        for candidate in candidates[: self.config.max_branching]:
            plan = self._evaluate_candidate(
                game_state, candidate, current_turn, remaining_turns, available_cash
            )
            if plan.value_per_turn > best_plan.value_per_turn:
                best_plan = plan

        return best_plan

    def _default_plan(self, turn: int) -> Plan:
        return Plan(
            steps=[PlanStep(turn=turn, action_type="pass")],
            expected_value=0.0,
            required_capital=0.0,
            required_workers=1,
            completion_turns=1,
            confidence=1.0,
            description="Default PASS fallback",
        )

    def _generate_lookahead_candidates(
        self,
        game_state: Any,
        current_turn: int,
        remaining_turns: int,
        available_cash: float,
    ) -> list[dict[str, Any]]:
        """Generate candidate immediate actions for lookahead evaluation."""
        candidates: list[dict[str, Any]] = []

        # Harvest mature crops
        candidates.append({
            "action_type": "harvest",
            "priority": 100,
            "immediate_value": self._estimate_harvest_value(game_state),
        })

        # Plant seeds (if available)
        seed_value = self._estimate_plant_value(game_state, available_cash, remaining_turns)
        if seed_value > 0:
            candidates.append({
                "action_type": "plant",
                "priority": 60,
                "immediate_value": seed_value,
            })

        # Water existing plants
        water_value = self._estimate_water_value(game_state)
        if water_value > 0:
            candidates.append({
                "action_type": "water",
                "priority": 50,
                "immediate_value": water_value,
            })

        # Sell shed items
        sell_value = self._estimate_sell_value(game_state)
        if sell_value > 0:
            candidates.append({
                "action_type": "sell",
                "priority": 40,
                "immediate_value": sell_value,
            })

        # Buy seeds
        buy_value = self._estimate_buy_seed_value(game_state, available_cash, remaining_turns)
        if buy_value > 0:
            candidates.append({
                "action_type": "buy_seed",
                "priority": 30,
                "immediate_value": buy_value,
            })

        # Buy land
        land_value = self._estimate_land_value(game_state, available_cash, remaining_turns)
        if land_value > 0:
            candidates.append({
                "action_type": "buy_land",
                "priority": 20,
                "immediate_value": land_value,
            })

        candidates.append({
            "action_type": "pass",
            "priority": 0,
            "immediate_value": 0.0,
        })

        return sorted(candidates, key=lambda c: (-c["priority"], -c["immediate_value"]))

    def _evaluate_candidate(
        self,
        game_state: Any,
        candidate: dict[str, Any],
        current_turn: int,
        remaining_turns: int,
        available_cash: float,
    ) -> Plan:
        """Evaluate a candidate action with simple lookahead."""
        action_type = candidate["action_type"]
        immediate = candidate["immediate_value"]

        # Simple lookahead: estimate next-turn value
        future_value = self._estimate_future_value(
            game_state, action_type, remaining_turns
        )

        total_value = immediate + future_value * 0.8  # discount future
        plan = Plan(
            steps=[PlanStep(turn=current_turn, action_type=action_type)],
            expected_value=total_value,
            expected_profit=immediate,
            required_capital=0.0,
            required_workers=1,
            completion_turns=1,
            confidence=0.8 if immediate > 0 else 0.5,
            description=f"Lookahead: {action_type} (immediate={immediate:.1f}, future={future_value:.1f})",
        )
        return plan

    def _estimate_harvest_value(self, game_state: Any) -> float:
        if not game_state:
            return 0.0
        farm = game_state.farm if hasattr(game_state, "farm") else None
        if farm is None:
            return 0.0
        for tile in getattr(farm, "tiles", {}).values():
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop_type = tile.get("crop", "")
                base_price = {"WHEAT": 10, "CARROT": 20, "TOMATO": 25,
                              "STRAWBERRY": 50, "MELON": 80}.get(crop_type, 10)
                yield_units = tile.get("yield_units", 0)
                if yield_units > 0:
                    return float(base_price * yield_units)
        return 0.0

    def _estimate_plant_value(
        self, game_state: Any, cash: float, remaining_turns: int
    ) -> float:
        seeds = (game_state.private.get("seeds", {}) if game_state and hasattr(game_state, "private")
                 else {})
        day = getattr(game_state, "current_day", lambda: 0)()
        best = 0.0
        for crop_type, params in CROP_PARAMS.items():
            if seeds.get(crop_type, 0) <= 0:
                continue
            if params.get("seed_cost", 999) > cash:
                continue
            growth = params.get("max_yield_day", 10) - day
            if growth <= 0 or growth > remaining_turns:
                continue
            price = params.get("base_price", 10)
            yield_amt = params.get("base_yield", 1)
            best = max(best, float(price * yield_amt) - params.get("seed_cost", 10))
        return best

    def _estimate_water_value(self, game_state: Any) -> float:
        if not game_state:
            return 0.0
        farm = getattr(game_state, "farm", None)
        if farm is None:
            return 0.0
        for tile in getattr(farm, "tiles", {}).values():
            if isinstance(tile, dict) and tile.get("kind") == "PLANT":
                crop_type = tile.get("crop", "")
                watered = tile.get("watered_today", True)
                yield_units = tile.get("yield_units", 0)
                if not watered and yield_units > 0:
                    bonus = CROP_PARAMS.get(crop_type, {}).get("bonus_yield_per_water", 1)
                    price = {"WHEAT": 10, "CARROT": 20, "TOMATO": 25,
                             "STRAWBERRY": 50, "MELON": 80}.get(crop_type, 10)
                    return float(price * bonus)
        return 0.0

    def _estimate_sell_value(self, game_state: Any) -> float:
        if not game_state:
            return 0.0
        shed = (game_state.private.get("shed", {}) if hasattr(game_state, "private") else {})
        if not shed:
            return 0.0
        market = game_state.market if hasattr(game_state, "market") else None
        prices = market.prices if market and hasattr(market, "prices") else {}
        total = 0.0
        for item, count in shed.items():
            price = prices.get(item, {"WHEAT": 10}.get(item, 5))
            total += count * price
        return total

    def _estimate_buy_seed_value(
        self, game_state: Any, cash: float, remaining_turns: int
    ) -> float:
        seeds = (game_state.private.get("seeds", {}) if game_state and hasattr(game_state, "private")
                 else {})
        day = getattr(game_state, "current_day", lambda: 0)()
        market = game_state.market if hasattr(game_state, "market") else None
        prices = market.prices if market and hasattr(market, "prices") else {}
        best = 0.0
        for crop_type, params in CROP_PARAMS.items():
            seed_cost = params.get("seed_cost", 999)
            if seeds.get(crop_type, 0) > 0:
                continue  # already have seeds
            if seed_cost > cash:
                continue
            growth = params.get("max_yield_day", 10) - day
            if growth <= 0 or growth > remaining_turns:
                continue
            price = prices.get(crop_type, params.get("base_price", 10))
            yield_amt = params.get("base_yield", 1)
            roi = (price * yield_amt - seed_cost) / max(1, seed_cost)
            if roi > 0:
                best = max(best, roi * 100)
        return best

    def _estimate_land_value(
        self, game_state: Any, cash: float, remaining_turns: int
    ) -> float:
        if not game_state:
            return 0.0
        farm = getattr(game_state, "farm", None)
        if farm is None:
            return 0.0
        unlocked = list(getattr(farm, "quadrants", []))
        land_costs = {"NE": 1000, "SW": 2000, "SE": 4000}
        for q in ["NE", "SW", "SE"]:
            if q in unlocked:
                continue
            cost = land_costs.get(q, 4000)
            if cost > cash:
                continue
            # Estimate: 25 new tiles, each worth estimated profit
            tiles = 25
            profit_per_tile = 5.0  # conservative estimate
            if tiles * profit_per_tile * remaining_turns / 720 > cost:
                return tiles * profit_per_tile * remaining_turns / 720
        return 0.0

    def _estimate_future_value(
        self, game_state: Any, action_type: str, remaining_turns: int
    ) -> float:
        """Estimate the value of the state after taking action_type."""
        if action_type == "plant":
            return 5.0  # future harvest
        if action_type == "water":
            return 3.0  # preserved yield
        if action_type == "buy_land":
            return 2.0 * remaining_turns / 720.0  # expanded capacity
        return 0.0

    def evaluate_plan(self, plan: Plan, game_state: Any, context: Any) -> PlanEvaluation:
        """Evaluate a plan against the current game state."""
        remaining_turns = getattr(context, "remaining_turns", 720) if context else 720
        available_cash = game_state.available_money() if game_state else 3000.0
        available_workers = len(game_state.available_workers()) if game_state else 1

        feasible = plan.is_feasible(
            available_cash=available_cash,
            available_workers=available_workers,
            remaining_turns=remaining_turns,
        ) if game_state else False

        total_score = plan.value_per_turn + plan.expected_profit * 0.5 - plan.risk * 10

        return PlanEvaluation(
            plan=plan,
            is_feasible=feasible,
            is_legal=True,
            total_score=total_score,
            immediate_score=plan.expected_profit,
            future_value=plan.expected_value - plan.expected_profit,
            explanation=plan.description,
        )
