"""Unit tests for Resource Optimizer (Stage 2)."""

from __future__ import annotations

from agent.optimization.resource_optimizer import ResourceOptimizer


class TestResourceOptimizer:
    def test_identify_no_bottlenecks(self) -> None:
        opt = ResourceOptimizer()
        bottlenecks = opt.identify_bottlenecks(
            cash=2000.0,
            workers=2,
            land_tiles=25,
            land_capacity=100,
            shed_items=50,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=600,
        )
        # No severe bottlenecks at these levels
        assert isinstance(bottlenecks, list)

    def test_identify_cash_bottleneck(self) -> None:
        opt = ResourceOptimizer()
        bottlenecks = opt.identify_bottlenecks(
            cash=100.0,
            workers=2,
            land_tiles=25,
            land_capacity=100,
            shed_items=50,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=600,
        )
        names = [b.name for b in bottlenecks]
        assert "cash" in names

    def test_identify_shed_capacity_bottleneck(self) -> None:
        opt = ResourceOptimizer()
        bottlenecks = opt.identify_bottlenecks(
            cash=2000.0,
            workers=2,
            land_tiles=25,
            land_capacity=100,
            shed_items=95,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=600,
        )
        names = [b.name for b in bottlenecks]
        assert "shed_capacity" in names

    def test_identify_time_bottleneck_endgame(self) -> None:
        opt = ResourceOptimizer()
        bottlenecks = opt.identify_bottlenecks(
            cash=2000.0,
            workers=2,
            land_tiles=25,
            land_capacity=100,
            shed_items=50,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=10,
        )
        names = [b.name for b in bottlenecks]
        assert "time" in names

    def test_bottleneck_severity_sorted(self) -> None:
        opt = ResourceOptimizer()
        bottlenecks = opt.identify_bottlenecks(
            cash=100.0,
            workers=1,
            land_tiles=25,
            land_capacity=100,
            shed_items=95,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=600,
        )
        if len(bottlenecks) >= 2:
            assert bottlenecks[0].severity >= bottlenecks[1].severity

    def test_is_endgame(self) -> None:
        opt = ResourceOptimizer()
        assert opt.is_endgame(30) is True
        assert opt.is_endgame(200) is False

    def test_is_late_game(self) -> None:
        opt = ResourceOptimizer()
        assert opt.is_late_game(100) is True
        assert opt.is_late_game(300) is False

    def test_is_early_game(self) -> None:
        opt = ResourceOptimizer()
        assert opt.is_early_game(3) is True
        assert opt.is_early_game(10) is False

    def test_primary_bottleneck(self) -> None:
        opt = ResourceOptimizer()
        bn = opt.primary_bottleneck(
            cash=100.0,
            workers=2,
            land_tiles=25,
            land_capacity=100,
            shed_items=50,
            shed_capacity=100,
            animal_count=2,
            animal_capacity=5,
            remaining_turns=600,
        )
        assert bn is not None
        assert bn.name == "cash"
