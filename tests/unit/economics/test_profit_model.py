"""Unit tests for the Profitability Engine (Stage 2)."""

from __future__ import annotations

from agent.economics.profit_model import (
    ProfitabilityEstimate,
    estimate_animal_profitability,
    estimate_crop_profitability,
)


class TestProfitabilityEstimate:
    def test_profitability_fields(self) -> None:
        est = ProfitabilityEstimate(
            name="wheat",
            seed_cost=10.0,
            expected_revenue=20.0,
            expected_yield=2,
            expected_sale_price=10.0,
            growth_duration=4,
            remaining_season=720,
        )
        assert est.total_cost == 10.0
        assert est.expected_profit == 10.0
        assert est.can_complete is True

    def test_roi_calculation(self) -> None:
        est = ProfitabilityEstimate(
            name="wheat",
            seed_cost=10.0,
            expected_revenue=30.0,
            expected_yield=2,
            expected_sale_price=10.0,
            growth_duration=4,
            remaining_season=720,
        )
        assert est.roi == 200.0  # (30-10)/10 * 100

    def test_zero_cost_zero_roi(self) -> None:
        est = ProfitabilityEstimate(
            name="test",
            seed_cost=0.0,
            expected_revenue=10.0,
            expected_yield=1,
            expected_sale_price=10.0,
            growth_duration=1,
            remaining_season=10,
        )
        assert est.roi == 0.0


class TestCropProfitability:
    def test_wheat_profitability(self) -> None:
        est = estimate_crop_profitability("WHEAT", current_day=0, remaining_turns=720)
        assert est.name == "crop_WHEAT"
        assert est.seed_cost == 10.0
        assert est.growth_duration > 0
        assert est.expected_profit > 0

    def test_carrot_profitability(self) -> None:
        est = estimate_crop_profitability("CARROT", current_day=0, remaining_turns=720)
        assert est.seed_cost == 20.0

    def test_crop_not_complete_if_too_late(self) -> None:
        est = estimate_crop_profitability("MELON", current_day=25, remaining_turns=100)
        # Melon max_yield_day is 10; planting at day 25 means growth_duration = -15
        assert est.growth_duration < 0 or est.growth_duration == 0

    def test_unknown_crop_defaults_to_wheat(self) -> None:
        est = estimate_crop_profitability("UNKNOWN", current_day=0, remaining_turns=720)
        assert est.seed_cost == 10.0


class TestAnimalProfitability:
    def test_goose_profitability(self) -> None:
        est = estimate_animal_profitability("GOOSE", current_day=0, remaining_turns=720)
        assert est.name == "animal_GOOSE"
        assert est.seed_cost == 30.0  # purchase cost
        assert est.feed_cost > 0

    def test_cow_profitability(self) -> None:
        est = estimate_animal_profitability("COW", current_day=0, remaining_turns=720)
        assert est.seed_cost == 50.0

    def test_unknown_animal_defaults_to_goose(self) -> None:
        est = estimate_animal_profitability("UNKNOWN", current_day=0, remaining_turns=720)
        assert est.seed_cost == 30.0
