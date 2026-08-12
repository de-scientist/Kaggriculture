from agent.domain import crop as crop_domain
from agent.domain.position import Position
from agent.domain.tile import Tile
from agent.services import crop_service


def test_plant_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    result = crop_service.plant(tile, "WHEAT", day=0)
    assert result.crop is not None
    assert result.crop.crop_type == "WHEAT"


def test_plant_on_occupied_tile_raises() -> None:
    pos = Position(0, 0)
    existing_crop = crop_domain.Crop(crop_type="WHEAT", planted_day=0)
    tile = Tile(position=pos).with_crop(existing_crop)
    try:
        crop_service.plant(tile, "CARROT", day=0)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def test_water_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    result = crop_service.water(planted)
    crop = result.crop
    assert crop is not None
    assert crop.watered_today is True


def test_water_harvested_crop_raises() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    harvested = crop_service.harvest(planted, current_day=2)
    try:
        crop_service.water(harvested)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def test_fertilize_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    result = crop_service.fertilize(planted, day=0)
    crop = result.crop
    assert crop is not None
    assert crop.fertilized_until_day == 3


def test_harvest_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    watered = crop_service.water(planted)
    result = crop_service.harvest(watered, current_day=2)
    crop = result.crop
    assert crop is not None
    assert crop.is_harvested is True


def test_harvest_immature_crop_raises() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    try:
        crop_service.harvest(planted)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def test_can_plant_empty_tile() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    assert crop_service.can_plant(tile) is True


def test_can_plant_occupied_tile() -> None:
    pos = Position(0, 0)
    existing_crop = crop_domain.Crop(crop_type="WHEAT", planted_day=0)
    tile = Tile(position=pos).with_crop(existing_crop)
    assert crop_service.can_plant(tile) is False


def test_can_harvest_mature_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    assert crop_service.can_harvest(planted, day=2) is True


def test_can_harvest_immature_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    assert crop_service.can_harvest(planted, day=1) is False


def test_expected_profit() -> None:
    result = crop_service.expected_profit("WHEAT", day=2, sell_price=15.0, seed_cost=10.0)
    assert result == 5.0


def test_growth_progress() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    assert crop_service.growth_progress(planted, day=0) == 0.0
    assert crop_service.growth_progress(planted, day=5) == 1.0


def test_needs_water() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    assert crop_service.needs_water(planted) is True
    watered = crop_service.water(planted)
    assert crop_service.needs_water(watered) is False


def test_needs_fertilizer() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    assert crop_service.needs_fertilizer(planted, day=0) is True
    fertilized = crop_service.fertilize(planted, day=0)
    assert crop_service.needs_fertilizer(fertilized, day=2) is False


def test_empty_tiles() -> None:
    pos = Position(0, 0)
    empty_tile = Tile(position=pos)
    crop = crop_domain.Crop(crop_type="WHEAT", planted_day=0)
    occupied_tile = Tile(position=Position(1, 0)).with_crop(crop)
    result = crop_service.empty_tiles([empty_tile, occupied_tile])
    assert len(result) == 1
    assert result[0].position == pos


def test_highest_roi_crop() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    planted = crop_service.plant(tile, "WHEAT", day=0)
    result = crop_service.highest_roi_crop(
        [planted],
        day=2,
        prices={"WHEAT": 15.0},
        costs={"WHEAT": 10.0},
    )
    assert result == "WHEAT"


def test_highest_roi_crop_no_crops() -> None:
    pos = Position(0, 0)
    tile = Tile(position=pos)
    result = crop_service.highest_roi_crop(
        [tile],
        day=2,
        prices={"WHEAT": 15.0},
        costs={"WHEAT": 10.0},
    )
    assert result is None
