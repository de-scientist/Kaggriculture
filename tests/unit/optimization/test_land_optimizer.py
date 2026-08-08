"""Unit tests for Land Optimizer (Stage 2)."""
from __future__ import annotations

from agent.optimization.land_optimizer import LandOptimizer, LandInvestment


class TestLandOptimizer:
    def test_evaluate_expansion_no_unlocked(self) -> None:
        opt = LandOptimizer()
        recs = opt.evaluate_expansion(
            available_cash=3000.0,
            unlocked_quadrants=["NW"],
            remaining_turns=720,
            farm_profit_per_turn=5.0,
            tile_count=25,
        )
        assert len(recs) > 0
        assert all(r.quadrant in ("NE", "SW", "SE") for r in recs)

    def test_evaluate_expansion_already_unlocked(self) -> None:
        opt = LandOptimizer()
        recs = opt.evaluate_expansion(
            available_cash=10000.0,
            unlocked_quadrants=["NW", "NE", "SW", "SE"],
            remaining_turns=720,
            farm_profit_per_turn=5.0,
            tile_count=100,
        )
        assert recs == []

    def test_evaluate_expansion_not_affordable(self) -> None:
        opt = LandOptimizer()
        recs = opt.evaluate_expansion(
            available_cash=100.0,
            unlocked_quadrants=["NW"],
            remaining_turns=720,
            farm_profit_per_turn=5.0,
            tile_count=25,
        )
        assert recs == []

    def test_next_best(self) -> None:
        opt = LandOptimizer()
        rec = opt.next_best(
            available_cash=3000.0,
            unlocked_quadrants=["NW"],
            remaining_turns=720,
            farm_profit_per_turn=10.0,
            tile_count=25,
        )
        assert rec is not None
        assert rec.quadrant == "NE"  # cheapest first

    def test_next_best_none(self) -> None:
        opt = LandOptimizer()
        rec = opt.next_best(
            available_cash=100.0,
            unlocked_quadrants=["NW", "NE", "SW", "SE"],
            remaining_turns=720,
            farm_profit_per_turn=10.0,
            tile_count=100,
        )
        assert rec is None

    def test_land_investment_viable(self) -> None:
        inv = LandInvestment(
            quadrant="NE",
            cost=1000.0,
            expected_additional_profit=5.0,
            payback_turns=200.0,
            roi=50.0,
            remaining_turns=720,
            can_afford=True,
            confidence=0.8,
            reason="test",
        )
        assert inv.is_viable is True

    def test_land_investment_not_viable(self) -> None:
        inv = LandInvestment(
            quadrant="SE",
            cost=4000.0,
            expected_additional_profit=1.0,
            payback_turns=4000.0,
            roi=10.0,
            remaining_turns=100,
            can_afford=True,
            confidence=0.1,
            reason="test",
        )
        assert inv.is_viable is False
