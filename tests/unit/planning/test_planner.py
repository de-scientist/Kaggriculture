"""Unit tests for Planning/Planner (Stage 2)."""

from __future__ import annotations

from agent.domain.game_state import GameState
from agent.planning.plan import Plan, PlanEvaluation, PlanStep
from agent.planning.planner import Planner, PlannerConfig


class TestPlanStep:
    def test_worker_op_pass(self) -> None:
        step = PlanStep(turn=0, action_type="pass")
        assert step.worker_op == ("PASS",)

    def test_worker_op_plant(self) -> None:
        step = PlanStep(turn=0, action_type="plant")
        assert step.worker_op == ("PLANT",)

    def test_worker_op_harvest(self) -> None:
        step = PlanStep(turn=0, action_type="harvest")
        assert step.worker_op == ("HARVEST",)

    def test_worker_op_water(self) -> None:
        step = PlanStep(turn=0, action_type="water")
        assert step.worker_op == ("WATER",)


class TestPlan:
    def test_default_plan(self) -> None:
        plan = Plan()
        assert plan.steps == []
        assert plan.expected_value == 0.0
        assert plan.first_action is None

    def test_plan_with_steps(self) -> None:
        plan = Plan()
        plan.add_step(PlanStep(turn=0, action_type="pass"))
        assert len(plan.steps) == 1
        assert plan.first_action == ("PASS",)
        assert plan.completion_turns == 0

    def test_to_action_dict(self) -> None:
        plan = Plan(steps=[PlanStep(turn=0, action_type="pass")])
        action = plan.to_action_dict()
        assert action["farmer"] == ["PASS"]
        assert action["hands"] == []
        assert action["market"] == []

    def test_to_action_dict_empty(self) -> None:
        plan = Plan()
        action = plan.to_action_dict()
        assert action["farmer"] == ["PASS"]

    def test_is_feasible(self) -> None:
        plan = Plan(
            steps=[PlanStep(turn=0, action_type="pass")],
            required_capital=100.0,
            required_workers=1,
            completion_turns=1,
        )
        assert (
            plan.is_feasible(
                available_cash=500.0,
                available_workers=2,
                remaining_turns=720,
            )
            is True
        )

    def test_is_not_feasible_low_cash(self) -> None:
        plan = Plan(
            steps=[PlanStep(turn=0, action_type="buy_land")],
            required_capital=5000.0,
            required_workers=1,
            completion_turns=5,
        )
        assert (
            plan.is_feasible(
                available_cash=1000.0,
                available_workers=2,
                remaining_turns=720,
            )
            is False
        )

    def test_value_per_turn(self) -> None:
        plan = Plan(
            expected_value=100.0,
            completion_turns=10,
        )
        assert plan.value_per_turn == 10.0

    def test_value_per_turn_zero_duration(self) -> None:
        plan = Plan(expected_value=100.0, completion_turns=0)
        assert plan.value_per_turn == 0.0


class TestPlanner:
    def test_plan_with_disabled(self) -> None:
        planner = Planner(config=PlannerConfig(enable_planning=False))
        state = GameState(player=0, step=0)
        plan = planner.plan(state, 0, 720, 3000.0)
        assert plan.steps[0].action_type == "pass"

    def test_plan_basic(self) -> None:
        planner = Planner(
            config=PlannerConfig(
                horizon_turns=5,
                max_rollouts=10,
                max_branching=8,
                enable_planning=True,
            )
        )
        state = GameState(player=0, step=0)
        plan = planner.plan(state, 0, 720, 3000.0)
        assert isinstance(plan, Plan)
        assert len(plan.steps) >= 1

    def test_plan_evaluation(self) -> None:
        planner = Planner()
        state = GameState(player=0, step=0)
        plan = Plan(
            steps=[PlanStep(turn=0, action_type="pass")],
            expected_value=10.0,
            required_capital=0.0,
            required_workers=1,
            completion_turns=1,
        )
        eval_result = planner.evaluate_plan(plan, state, None)
        assert isinstance(eval_result, PlanEvaluation)
        assert eval_result.is_feasible is True
