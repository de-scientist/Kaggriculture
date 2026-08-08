"""Unit tests for Animal Optimizer (Stage 2)."""
from __future__ import annotations

from agent.optimization.animal_optimizer import AnimalOptimizer, AnimalRecommendation


class TestAnimalOptimizer:
    def test_evaluate_purchase_no_cash(self) -> None:
        opt = AnimalOptimizer()
        recs = opt.evaluate_purchase(
            current_day=0,
            remaining_turns=720,
            market_prices={},
            available_cash=0.0,
            existing_animals={},
            has_structure={},
        )
        assert recs == []

    def test_evaluate_purchase_with_structure(self) -> None:
        opt = AnimalOptimizer()
        recs = opt.evaluate_purchase(
            current_day=0,
            remaining_turns=720,
            market_prices={"EGG": 30},
            available_cash=100.0,
            existing_animals={},
            has_structure={"COOP": True},
        )
        assert len(recs) > 0
        assert recs[0].animal_type == "GOOSE"

    def test_evaluate_purchase_no_structure(self) -> None:
        opt = AnimalOptimizer()
        recs = opt.evaluate_purchase(
            current_day=0,
            remaining_turns=720,
            market_prices={"EGG": 30, "MILK": 50, "WOOL": 40},
            available_cash=1000.0,
            existing_animals={},
            has_structure={},
        )
        assert recs == []  # no structures built

    def test_best_purchase(self) -> None:
        opt = AnimalOptimizer()
        rec = opt.best_purchase(
            current_day=0,
            remaining_turns=720,
            market_prices={"EGG": 30, "MILK": 50},
            available_cash=200.0,
            existing_animals={},
            has_structure={"COOP": True, "PASTURE": True},
        )
        assert rec is not None
        assert isinstance(rec, AnimalRecommendation)

    def test_best_purchase_none(self) -> None:
        opt = AnimalOptimizer()
        rec = opt.best_purchase(
            current_day=0,
            remaining_turns=720,
            market_prices={},
            available_cash=0.0,
            existing_animals={},
            has_structure={},
        )
        assert rec is None
