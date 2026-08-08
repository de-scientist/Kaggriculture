"""Unit tests for the Crop domain model (chapter 9)."""
from __future__ import annotations

import pytest

from agent.domain.crop import Crop


class TestCropConstruction:
    def test_default_values(self) -> None:
        crop = Crop(crop_type="WHEAT")
        assert crop.crop_type == "WHEAT"
        assert crop.planted_day == 0
        assert crop.watered_today is False
        assert crop.consecutive_unwatered == 0
        assert crop.yield_units == 0
        assert crop.is_harvested is False
        assert crop.fertilized_until_day == -1

    def test_custom_values(self) -> None:
        crop = Crop(crop_type="CARROT", planted_day=3, max_lifespan_step=15)
        assert crop.planted_day == 3
        assert crop.max_lifespan_step == 15

    def test_repr_contains_key_fields(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=2)
        assert "WHEAT" in repr(crop)


class TestCropMaturity:
    @pytest.mark.parametrize("current_day,planted_day,expected", [
        (0, 0, False),
        (1, 0, False),
        (2, 0, True),
        (3, 0, True),
        (2, 2, False),
        (3, 1, True),
        (1, 5, False),
    ])
    def test_is_mature(self, current_day: int, planted_day: int, expected: bool) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=planted_day)
        assert crop.is_mature(current_day) is expected

    def test_is_alive_within_lifespan(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0, max_lifespan_step=10)
        assert crop.is_alive(5) is True
        assert crop.is_alive(11) is True
        assert crop.is_alive(12) is False

    def test_is_in_bonus_window(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0, max_lifespan_step=10)
        # bonus window: ceil(10/2) = 5 .. 10
        assert crop.is_in_bonus_window(5) is True
        assert crop.is_in_bonus_window(7) is True
        assert crop.is_in_bonus_window(10) is True
        assert crop.is_in_bonus_window(4) is False
        assert crop.is_in_bonus_window(11) is False


class TestCropWatering:
    def test_water_sets_watered_today(self) -> None:
        crop = Crop(crop_type="WHEAT")
        watered = crop.water()
        assert watered.watered_today is True
        assert watered.consecutive_unwatered == 0

    def test_water_preserves_state(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=1, max_lifespan_step=10)
        watered = crop.water()
        assert watered.planted_day == 1
        assert watered.crop_type == "WHEAT"

    def test_water_harvested_crop_raises(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        harvested = crop.harvest()
        with pytest.raises(ValueError, match="Cannot water a harvested crop"):
            harvested.water()

    def test_skip_water_increments_consecutive(self) -> None:
        crop = Crop(crop_type="WHEAT")
        skipped = crop.skip_water()
        assert skipped.watered_today is False
        assert skipped.consecutive_unwatered == 1


class TestCropFertilizing:
    def test_fertilize_sets_window(self) -> None:
        crop = Crop(crop_type="WHEAT")
        fertilized = crop.fertilize(current_day=0)
        assert fertilized.fertilized_until_day == 3

    def test_fertilize_preserves_watered_today(self) -> None:
        crop = Crop(crop_type="WHEAT")
        watered = crop.water()
        fertilized = watered.fertilize(current_day=0)
        assert fertilized.watered_today is True
        assert fertilized.fertilized_until_day == 3


class TestCropGrowth:
    def test_grow_with_water_bonus(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        watered = crop.water()
        grown = watered.grow(current_day=5)
        assert grown.yield_units == 1

    def test_grow_with_water_and_fertilizer_bonus(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        watered = crop.water()
        fertilized = watered.fertilize(current_day=0)
        grown = fertilized.grow(current_day=1)
        assert grown.yield_units == 2

    def test_grow_without_water(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        grown = crop.grow(current_day=5)
        assert grown.yield_units == 0


class TestCropHarvest:
    def test_harvest_mature_crop(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        watered = crop.water()
        grown = watered.grow(current_day=2)
        harvested = grown.harvest()
        assert harvested.is_harvested is True

    def test_harvest_unharvested_twice_raises(self) -> None:
        crop = Crop(crop_type="WHEAT", planted_day=0)
        watered = crop.water()
        grown = watered.grow(current_day=2)
        harvested = grown.harvest()
        with pytest.raises(ValueError, match="already harvested"):
            harvested.harvest()
