from __future__ import annotations


def build_move(direction: str) -> list:
    return [direction]


def build_pass() -> list:
    return ["PASS"]


def build_plant(crop_type: str) -> list:
    return ["PLANT", crop_type]


def build_water() -> list:
    return ["WATER"]


def build_harvest() -> list:
    return ["HARVEST"]


def build_fertilize() -> list:
    return ["FERTILIZE"]


def build_dig() -> list:
    return ["DIG"]


def build_build_coop() -> list:
    return ["BUILD_COOP"]


def build_build_pasture() -> list:
    return ["BUILD_PASTURE"]


def build_feed() -> list:
    return ["FEED"]


def build_collect_fertilizer() -> list:
    return ["COLLECT_FERTILIZER"]


def build_care() -> list:
    return ["CARE"]


def build_pickup(item: str, count: int = 1) -> list:
    return ["PICKUP", item, count]


def build_place(item: str, count: int = 1) -> list:
    return ["PLACE", item, count]


def build_drop() -> list:
    return ["DROP"]


def build_buy_seed(crop: str, count: int) -> list:
    return ["BUY_SEED", crop, count]


def build_buy_product(item: str, count: int) -> list:
    return ["BUY_PRODUCT", item, count]


def build_buy_animal(animal: str, count: int) -> list:
    return ["BUY_ANIMAL", animal, count]


def build_sell(item: str, count: int) -> list:
    return ["SELL", item, count]


def build_hire() -> list:
    return ["HIRE"]


def build_buy_land() -> list:
    return ["BUY_LAND"]
