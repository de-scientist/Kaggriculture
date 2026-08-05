from agent.domain.crop import Crop


def plant(tile: object, crop_type: str, day: int) -> tuple[object, Crop]:
    crop = Crop(crop_type=crop_type, planted_day=day)
    return tile, crop


def water(crop: Crop) -> Crop:
    return crop.water()


def fertilize(crop: Crop, day: int) -> Crop:
    return crop.fertilize(day)


def grow(crop: Crop, day: int) -> Crop:
    return crop.grow(day)


def harvest(crop: Crop) -> Crop:
    return crop.harvest()


def skip_water(crop: Crop) -> Crop:
    return crop.skip_water()