"""Unit tests for the ActionAdapter (chapter 9)."""
from __future__ import annotations

import pytest

from agent.adapters.action_adapter import ActionAdapter

from tests.fixtures.actions import (
    build_coop_action,
    build_pasture_action,
    buy_animal_action,
    buy_land_action,
    buy_seed_action,
    collect_fertilizer_action,
    dig_action,
    drop_action,
    fertilize_action,
    feed_action,
    harvest_action,
    hire_action,
    movement_action,
    pass_action,
    plant_action,
    sell_action,
    water_action,
)


@pytest.fixture
def adapter() -> ActionAdapter:
    return ActionAdapter()


class TestActionAdapterConvert:
    def test_convert_pass_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(pass_action())
        assert result["farmer"] == ["PASS"]
        assert result["hands"] == []
        assert result["market"] == []

    def test_convert_plant_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(plant_action("CARROT"))
        assert result["farmer"] == ["PLANT", "CARROT"]

    def test_convert_water_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(water_action())
        assert result["farmer"] == ["WATER"]

    def test_convert_harvest_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(harvest_action())
        assert result["farmer"] == ["HARVEST"]

    def test_convert_fertilize_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(fertilize_action())
        assert result["farmer"] == ["FERTILIZE"]

    def test_convert_sell_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(sell_action("WHEAT", 5))
        assert result["market"] == [["SELL", "WHEAT", 5]]

    def test_convert_buy_seed_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(buy_seed_action("WHEAT", 2))
        assert result["market"] == [["BUY_SEED", "WHEAT", 2]]

    def test_convert_buy_animal_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(buy_animal_action("COW", 1))
        assert result["market"] == [["BUY_ANIMAL", "COW", 1]]

    def test_convert_hire_action(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(hire_action())
        assert result["market"] == [["HIRE"]]


class TestActionAdapterMovement:
    @pytest.mark.parametrize("direction", ["NORTH", "SOUTH", "EAST", "WEST"])
    def test_convert_movement(self, adapter: ActionAdapter, direction: str) -> None:
        result = adapter.convert(movement_action(direction))
        assert result["farmer"] == [direction]


class TestActionAdapterBuilding:
    def test_convert_build_coop(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(build_coop_action())
        assert result["farmer"] == ["BUILD_COOP"]

    def test_convert_build_pasture(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(build_pasture_action())
        assert result["farmer"] == ["BUILD_PASTURE"]


class TestActionAdapterAnimals:
    def test_convert_feed(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(feed_action())
        assert result["farmer"] == ["FEED"]

    def test_convert_care(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": ["CARE"], "hands": [], "market": []})
        assert result["farmer"] == ["CARE"]

    def test_convert_collect_fertilizer(self, adapter: ActionAdapter) -> None:
        result = adapter.convert(collect_fertilizer_action())
        assert result["farmer"] == ["COLLECT_FERTILIZER"]


class TestActionAdapterEdgeCases:
    def test_convert_empty_action_uses_pass(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"hands": [], "market": []})
        assert result["farmer"] == ["PASS"]

    def test_convert_none_farmer_defaults_pass(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": None, "hands": [], "market": []})
        assert result["farmer"] == ["PASS"]

    def test_convert_empty_hand_defaults_pass(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": ["PASS"], "hands": [[]], "market": []})
        assert result["hands"] == [["PASS"]]

    def test_convert_empty_market_op_skipped(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": ["PASS"], "hands": [], "market": [[]]})
        assert result["market"] == []

    def test_convert_unknown_farmer_action_defaults_pass(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": ["BOGUS"], "hands": [], "market": []})
        assert result["farmer"] == ["PASS"]

    def test_convert_unknown_market_action_skipped(self, adapter: ActionAdapter) -> None:
        result = adapter.convert({"farmer": ["PASS"], "hands": [], "market": [["BOGUS"]]})
        assert result["market"] == []
