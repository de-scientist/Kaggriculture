"""Stage 2 — Multi-turn planner.

Builds multi-turn plans over a configurable horizon and evaluates candidate
actions against the current economic state. The planner never consumes future
information: every step is derived from the supplied game state and candidate
actions available at the current turn.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.planning.plan import Plan, PlanEvaluation, PlanStep


@dataclass
class PlannerConfig:
    """Configuration for the multi-turn planner.

    Attributes:
        horizon_turns: Number of turns to look ahead.
        max_rollouts: Maximum rollouts used by search-based planning.
        max_branching: Maximum candidate actions considered per turn.
        enable_planning: When False the planner returns a single PASS step.
        risk_aversion: Extra penalty applied to risky plans (0..1).
        compute_budget_ms: Soft wall-clock budget for a single plan call.
    """

    horizon_turns: int = 5
    max_rollouts: int = 10
    max_branching: int = 8
    enable_planning: bool = True
    risk_aversion: float = 0.0
    compute_budget_ms: float = 50.0


class Planner:
    """Multi-turn planner with configurable horizon and safe fallback.

    The planner produces :class:`Plan` objects whose steps are executable
    through the existing action validation layer. It degrades gracefully:
    if planning is disabled, the horizon is exhausted, or no candidate
    actions exist, it returns a plan containing a single PASS step.
    """

    def __init__(self, config: PlannerConfig | dict | None = None) -> None:
        self.config = self._coerce_config(config)

    @staticmethod
    def _coerce_config(config: PlannerConfig | dict | None) -> PlannerConfig:
        if config is None:
            return PlannerConfig()
        if isinstance(config, PlannerConfig):
            return config
        return PlannerConfig(
            horizon_turns=config.get("horizon_turns", 5),
            max_rollouts=config.get("max_rollouts", 10),
            max_branching=config.get("max_branching", 8),
            enable_planning=config.get("enable_planning", True),
            risk_aversion=config.get("risk_aversion", 0.0),
            compute_budget_ms=config.get("compute_budget_ms", 50.0),
        )

    def plan(
        self,
        state: Any,
        current_turn: int = 0,
        total_turns: int = 720,
        available_cash: float = 0.0,
        *,
        context: Any = None,
        actions: list[Any] | None = None,
    ) -> Plan:
        """Generate a multi-turn plan starting at ``current_turn``.

        Args:
            state: Canonical game state (or an object exposing ``game_state``).
            current_turn: Absolute turn the plan starts at.
            total_turns: Absolute final turn of the season.
            available_cash: Cash available for capital-constrained steps.
            context: Optional decision context used for scoring.
            actions: Candidate actions to choose from during the horizon.
        """
        if not self.config.enable_planning:
            return Plan(steps=[PlanStep(turn=current_turn, action_type="pass")])

        game_state = self._resolve_game_state(state, context)
        steps = self._greedy_steps(
            game_state=game_state,
            current_turn=current_turn,
            total_turns=total_turns,
            available_cash=available_cash,
            actions=actions,
        )
        expected_profit = sum(self._step_value(step) for step in steps)
        completion = (steps[-1].turn - current_turn) if steps else 0
        return Plan(
            steps=steps,
            expected_value=max(0.0, expected_profit),
            expected_profit=expected_profit,
            required_capital=self._required_capital(steps),
            required_workers=max(1, len(steps)),
            completion_turns=max(0, completion),
            confidence=0.5,
            risk=self.config.risk_aversion,
            description=f"greedy_horizon={self.config.horizon_turns}",
        )

    def evaluate_plan(
        self,
        plan: Plan,
        state: Any,
        context: Any = None,
    ) -> PlanEvaluation:
        """Evaluate a plan for feasibility and expected value."""
        game_state = self._resolve_game_state(state, context)
        available_cash = self._available_cash(game_state)
        available_workers = self._available_workers(game_state)
        remaining_turns = self._remaining_turns(game_state, context)
        is_feasible = plan.is_feasible(available_cash, available_workers, remaining_turns)
        future_value = max(0.0, plan.expected_value)
        risk_penalty = plan.risk * self.config.risk_aversion
        return PlanEvaluation(
            plan=plan,
            is_feasible=is_feasible,
            is_legal=True,
            total_score=future_value - risk_penalty,
            immediate_score=0.0,
            future_value=future_value,
            explanation="plan_evaluation",
        )

    def _greedy_steps(
        self,
        game_state: Any,
        current_turn: int,
        total_turns: int,
        available_cash: float,
        actions: list[Any] | None,
    ) -> list[PlanStep]:
        steps: list[PlanStep] = []
        candidates = list(actions or [])
        end = min(current_turn + self.config.horizon_turns, total_turns)
        for turn in range(current_turn, end):
            action = self._best_action(candidates, available_cash)
            if action is None:
                steps.append(PlanStep(turn=turn, action_type="pass"))
            else:
                steps.append(self._to_step(action, turn))
        if not steps:
            steps.append(PlanStep(turn=current_turn, action_type="pass"))
        return steps

    def _best_action(self, candidates: list[Any], available_cash: float) -> Any | None:
        affordable = [a for a in candidates if a.estimated_cost <= max(0.0, available_cash)]
        pool = affordable or candidates
        if not pool:
            return None
        return max(pool, key=lambda a: (a.net_value, a.id))

    @staticmethod
    def _to_step(action: Any, turn: int) -> PlanStep:
        params: dict[str, Any] = {}
        net_value = getattr(action, "net_value", 0.0)
        if net_value:
            params["net_value"] = net_value
        estimated_cost = getattr(action, "estimated_cost", 0.0)
        if estimated_cost:
            params["estimated_cost"] = estimated_cost
        return PlanStep(
            turn=turn,
            action_type=getattr(action, "action_type", "pass"),
            target_position=getattr(action, "target_position", None),
            target_entity=getattr(action, "target_entity", ""),
            params=params,
        )

    @staticmethod
    def _step_value(step: PlanStep) -> float:
        return float(step.params.get("net_value", 0.0))

    @staticmethod
    def _required_capital(steps: list[PlanStep]) -> float:
        return sum(float(s.params.get("estimated_cost", 0.0)) for s in steps)

    @staticmethod
    def _resolve_game_state(state: Any, context: Any) -> Any:
        for source in (state, context):
            if source is None:
                continue
            nested = getattr(source, "game_state", None)
            if nested is not None:
                return nested
        return state

    @staticmethod
    def _available_cash(game_state: Any) -> float:
        if game_state is None:
            return 0.0
        money = getattr(game_state, "available_money", None)
        if callable(money):
            return float(money())
        farm = getattr(game_state, "farm", None)
        if farm is not None:
            return float(getattr(farm, "money", 0.0))
        return 0.0

    @staticmethod
    def _available_workers(game_state: Any) -> int:
        count = 1
        if game_state is None:
            return count
        farm = getattr(game_state, "farm", None)
        if farm is not None:
            count += len(getattr(farm, "workers", []) or [])
        return count

    @staticmethod
    def _remaining_turns(game_state: Any, context: Any) -> int:
        if context is not None and getattr(context, "remaining_turns", None) is not None:
            return int(context.remaining_turns)
        if game_state is None:
            return 720
        remaining = getattr(game_state, "remaining_turns", None)
        if callable(remaining):
            return int(remaining())
        return 720
