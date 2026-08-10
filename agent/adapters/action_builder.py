from __future__ import annotations


def build_move(direction: str) -> list[str]:
    return [direction]


def build_pass() -> list[str]:
    return ["PASS"]


def build_plant(crop_type: str) -> list[str]:
    return ["PLANT", crop_type]


def build_water() -> list[str]:
    return ["WATER"]


def build_harvest() -> list[str]:
    return ["HARVEST"]


def build_fertilize() -> list[str]:
    return ["FERTILIZE"]


def build_dig() -> list[str]:
    return ["DIG"]


def build_build_coop() -> list[str]:
    return ["BUILD_COOP"]


def build_build_pasture() -> list[str]:
    return ["BUILD_PASTURE"]


def build_feed() -> list[str]:
    return ["FEED"]


def build_collect_fertilizer() -> list[str]:
    return ["COLLECT_FERTILIZER"]


def build_care() -> list[str]:
    return ["CARE"]


def build_pickup(item: str, count: int = 1) -> list[str | int]:
    return ["PICKUP", item, count]


def build_place(item: str, count: int = 1) -> list[str | int]:
    return ["PLACE", item, count]


def build_drop() -> list[str]:
    return ["DROP"]


def build_buy_seed(crop: str, count: int) -> list[str | int]:
    return ["BUY_SEED", crop, count]


def build_buy_product(item: str, count: int) -> list[str | int]:
    return ["BUY_PRODUCT", item, count]


def build_buy_animal(animal: str, count: int) -> list[str | int]:
    return ["BUY_ANIMAL", animal, count]


def build_sell(item: str, count: int) -> list[str | int]:
    return ["SELL", item, count]


def build_hire() -> list[str]:
    return ["HIRE"]


def build_buy_land() -> list[str]:
    return ["BUY_LAND"]
