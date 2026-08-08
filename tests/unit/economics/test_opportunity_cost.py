"""Unit tests for the Opportunity Cost Engine (Stage 2)."""
from __future__ import annotations

from agent.economics.opportunity_cost import (
    OpportunityCost,
    OpportunityCostEngine,
)


class TestOpportunityCost:
    def test_worker_opportunity_cost(self) -> None:
        engine = OpportunityCostEngine()
        cost = engine.worker_opportunity_cost(
            worker_id="farmer",
            current_action_value=10.0,
            alternative_actions=[("water", 15.0), ("plant", 5.0)],
        )
        assert cost.cost == 5.0  # 15 - 10
        assert "farmer" in cost.label

    def test_worker_opportunity_cost_no_better_alt(self) -> None:
        engine = OpportunityCostEngine()
        cost = engine.worker_opportunity_cost(
            worker_id="farmer",
            current_action_value=20.0,
            alternative_actions=[("water", 10.0), ("plant", 5.0)],
        )
        assert cost.cost == 0.0  # current is best

    def test_cash_opportunity_cost(self) -> None:
        engine = OpportunityCostEngine()
        cost = engine.cash_opportunity_cost(
            amount=1000.0,
            alternative_roi=10.0,
            remaining_turns=720,
        )
        assert cost.cost > 0.0
        assert "cash" in cost.label

    def test_land_opportunity_cost_viable(self) -> None:
        engine = OpportunityCostEngine()
        cost = engine.land_opportunity_cost(
            quadrant="NE",
            land_cost=1000.0,
            expected_additional_profit=5.0,
            remaining_turns=720,
        )
        assert cost.cost == 0.0  # payback within remaining turns

    def test_land_opportunity_cost_not_viable(self) -> None:
        engine = OpportunityCostEngine()
        cost = engine.land_opportunity_cost(
            quadrant="SE",
            land_cost=4000.0,
            expected_additional_profit=1.0,
            remaining_turns=10,
        )
        assert cost.cost == 4000.0  # payback too long

    def test_calculate_all(self) -> None:
        from agent.domain.game_state import GameState

        engine = OpportunityCostEngine()
        state = GameState(player=0, step=0)
        costs = engine.calculate_all(state, {})
        assert "cash_reserve" in costs
