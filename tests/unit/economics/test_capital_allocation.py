"""Unit tests for Capital Allocation Engine (Stage 2)."""

from __future__ import annotations

from agent.economics.capital_allocation import CapitalAllocation, CapitalAllocator


class TestCapitalAllocator:
    def test_allocate_prefers_high_roi(self) -> None:
        allocator = CapitalAllocator(min_cash_reserve=500.0)
        opps = [
            CapitalAllocation(
                category="seeds",
                amount=100.0,
                expected_roi=200.0,
                payback_turns=4,
                confidence=0.9,
                description="Wheat seeds",
            ),
            CapitalAllocation(
                category="land",
                amount=1000.0,
                expected_roi=50.0,
                payback_turns=20,
                confidence=0.7,
                description="NE quadrant",
            ),
        ]
        selected = allocator.allocate(available_cash=3000.0, opportunities=opps)
        assert len(selected) == 2  # both affordable after reserve
        assert selected[0].category == "seeds"  # higher ROI first

    def test_allocate_respects_reserve(self) -> None:
        allocator = CapitalAllocator(min_cash_reserve=500.0)
        opps = [
            CapitalAllocation(
                category="seeds",
                amount=3000.0,
                expected_roi=200.0,
                payback_turns=4,
                confidence=0.9,
                description="Wheat seeds",
            ),
        ]
        selected = allocator.allocate(available_cash=2000.0, opportunities=opps)
        assert len(selected) == 0  # cash below reserve

    def test_allocate_budget_exhausted(self) -> None:
        allocator = CapitalAllocator(min_cash_reserve=100.0)
        opps = [
            CapitalAllocation(
                category="a",
                amount=500.0,
                expected_roi=100.0,
                payback_turns=5,
                confidence=0.9,
                description="A",
            ),
            CapitalAllocation(
                category="b",
                amount=500.0,
                expected_roi=200.0,
                payback_turns=5,
                confidence=0.9,
                description="B",
            ),
        ]
        selected = allocator.allocate(available_cash=600.0, opportunities=opps)
        assert len(selected) == 1
        assert selected[0].category == "b"  # higher ROI fits

    def test_land_allocation_viable(self) -> None:
        allocator = CapitalAllocator(land_costs={"NE": 1000, "SW": 2000, "SE": 4000})
        result = allocator.land_allocation(
            cash=3000.0,
            expected_profit_per_turn=20.0,
            remaining_turns=720,
        )
        assert result is not None
        assert result.category == "land_NE"

    def test_land_allocation_not_affordable(self) -> None:
        allocator = CapitalAllocator(land_costs={"NE": 1000, "SW": 2000, "SE": 4000})
        result = allocator.land_allocation(
            cash=500.0,
            expected_profit_per_turn=20.0,
            remaining_turns=720,
        )
        assert result is None
