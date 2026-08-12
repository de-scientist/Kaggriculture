"""Unit tests for Crop Optimizer (Stage 2)."""

from __future__ import annotations

from agent.optimization.crop_optimizer import CropOptimizer, CropRecommendation


class TestCropOptimizer:
    def test_evaluate_planting_no_seeds(self) -> None:
        opt = CropOptimizer()
        recs = opt.evaluate_planting(
            current_day=0,
            remaining_turns=720,
            market_prices={},
            available_seeds={},
            available_cash=3000.0,
            planted_tiles={},
        )
        assert recs == []  # no seeds available

    def test_evaluate_planting_with_seeds(self) -> None:
        opt = CropOptimizer()
        recs = opt.evaluate_planting(
            current_day=0,
            remaining_turns=720,
            market_prices={"WHEAT": 10},
            available_seeds={"WHEAT": 5},
            available_cash=3000.0,
            planted_tiles={},
        )
        assert len(recs) > 0
        assert recs[0].crop_type == "WHEAT"

    def test_evaluate_planting_insufficient_cash(self) -> None:
        opt = CropOptimizer()
        recs = opt.evaluate_planting(
            current_day=0,
            remaining_turns=720,
            market_prices={"MELON": 80},
            available_seeds={"MELON": 1},
            available_cash=10.0,  # not enough for melon seed ($50)
            planted_tiles={},
        )
        assert recs == []

    def test_optimal_crop(self) -> None:
        opt = CropOptimizer()
        rec = opt.optimal_crop(
            current_day=0,
            remaining_turns=720,
            market_prices={"WHEAT": 10, "CARROT": 20},
            available_seeds={"WHEAT": 5, "CARROT": 3},
            available_cash=3000.0,
            planted_tiles={},
        )
        assert rec is not None
        # Carrot has higher base price but wheat is more affordable
        assert isinstance(rec, CropRecommendation)

    def test_optimal_crop_none(self) -> None:
        opt = CropOptimizer()
        rec = opt.optimal_crop(
            current_day=0,
            remaining_turns=720,
            market_prices={},
            available_seeds={},
            available_cash=0.0,
            planted_tiles={},
        )
        assert rec is None

    def test_portfolio(self) -> None:
        opt = CropOptimizer()
        recs = opt.portfolio(
            current_day=0,
            remaining_turns=720,
            market_prices={"WHEAT": 10, "CARROT": 20},
            available_seeds={"WHEAT": 5, "CARROT": 3},
            available_cash=3000.0,
            max_plantings=3,
        )
        assert len(recs) <= 3

    def test_plant_too_late(self) -> None:
        opt = CropOptimizer()
        # Melon needs day 0-10 planting, won't grow if planted at day 25
        recs = opt.evaluate_planting(
            current_day=25,
            remaining_turns=100,
            market_prices={"MELON": 80},
            available_seeds={"MELON": 1},
            available_cash=3000.0,
            planted_tiles={},
        )
        assert recs == []  # too late to plant melon
