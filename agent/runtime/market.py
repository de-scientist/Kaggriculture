"""Market-order planning: sell produce, buy seeds, hire hands, buy land.

Orders are returned in priority order (sells first, then hires, seeds, land)
and the engine only honors the first ``maxMarketOrdersPerTurn`` (default 10).
"""

from __future__ import annotations

from typing import Any

from .constants import ANIMALS, LAND_ORDER, LAND_PRICES, MARKET, SHED_CAPACITY, hire_cost
from .game import GameSnapshot
from .settings import RuntimeSettings
from .tasks import target_hands

_PRODUCT_SELL_ORDER = ["CARROT", "TOMATO", "WHEAT", "STRAWBERRY", "EGG", "MILK", "WOOL", "MELON"]


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sell_amounts(snapshot: GameSnapshot, settings: RuntimeSettings) -> dict[str, int]:
    """How many units of each product to sell this turn, product -> count."""
    shed = snapshot.shed()
    prices = snapshot.prices()
    occupancy = snapshot.shed_occupancy()
    high_water = int(settings.shed_high_watermark * SHED_CAPACITY)
    endgame = snapshot.day >= settings.endgame_sell_day or snapshot.is_final_day()
    out: dict[str, int] = {}
    for product in _PRODUCT_SELL_ORDER:
        count = _int(shed.get(product), 0)
        if count <= 0:
            continue
        base = int(MARKET[product]["base"])
        price = _num(prices.get(product), base)
        if product == "WHEAT":
            keep = 0 if endgame else settings.wheat_keep_buffer
            sell = max(0, count - keep)
        elif product == "MELON":
            if endgame or occupancy >= high_water:
                sell = count
            else:
                sell = min(count, settings.melon_sell_cap)
        else:
            if endgame or occupancy >= high_water or price >= settings.sell_min_ratio * base:
                sell = count
            else:
                continue
        if sell > 0:
            out[product] = sell
    return out


def plan_market_orders(snapshot: GameSnapshot, settings: RuntimeSettings) -> list[list[Any]]:
    """Return the ordered market order list (honoring the per-turn cap)."""
    cap = settings.max_market_orders
    orders: list[list[Any]] = []
    money = snapshot.money()
    reserve = settings.reserve_money

    # 1) Sales first: cash now, and early sales fetch scarcity premiums.
    for product, n in sell_amounts(snapshot, settings).items():
        if len(orders) < cap:
            orders.append(["SELL", product, n])

    # 2) Hire hands (cheap; they reset daily).
    n_hands = len(snapshot.hands())
    target = target_hands(snapshot, settings)
    while n_hands < target and len(orders) < cap:
        cost = hire_cost(n_hands)
        if money - reserve < cost:
            break
        orders.append(["HIRE"])
        money -= cost
        n_hands += 1

    # 3) Buy seeds for the crop we plan to plant (melon gate adapts to the
    #    opponent's melon plantings).
    crop = _planned_crop(snapshot, settings)
    if crop is not None:
        empty = len(snapshot.empty_tiles())
        have = snapshot.seed_count(crop)
        want = min(max(0, empty - have), settings.max_market_buy_seed_units)
        if want > 0 and len(orders) < cap:
            seed_cost = int(_planned_crop_seed_cost(crop))
            affordable = max(0, int((money - reserve) // seed_cost)) if seed_cost > 0 else 0
            buy = min(want, affordable)
            if buy > 0:
                orders.append(["BUY_SEED", crop, buy])
                money -= seed_cost * buy

    # 4) Animal procurement (opt-in).
    if settings.enable_animals:
        _plan_animal_buys(snapshot, settings, orders, money, reserve, cap)

    # 5) Land expansion last.
    unlocked = snapshot.unlocked()
    for idx, (quadrant, price) in enumerate(zip(LAND_ORDER, LAND_PRICES, strict=True)):
        if quadrant in unlocked:
            continue
        if snapshot.day >= settings.land_latest_day[idx]:
            break
        if money >= price * settings.land_budget_ratio and len(orders) < cap:
            orders.append(["BUY_LAND"])
            money -= price
            break

    return orders[:cap]


def _planned_crop(snapshot: GameSnapshot, settings: RuntimeSettings) -> str | None:
    from .crops import best_crop

    return best_crop(snapshot, settings)


def _planned_crop_seed_cost(crop: str) -> int:
    from .constants import CROPS

    return int(CROPS[crop]["seed"])


def _plan_animal_buys(
    snapshot: GameSnapshot,
    settings: RuntimeSettings,
    orders: list[list[Any]],
    money: float,
    reserve: float,
    cap: int,
) -> None:
    prices = snapshot.prices()
    wheat_ratio = _num(prices.get("WHEAT"), 25) / 25
    if wheat_ratio > settings.cow_max_wheat_ratio:
        return
    cows_placed = _count_animal(snapshot, "COW")
    cows_owned = _int(snapshot.shed().get("COW"), 0)
    if (
        snapshot.day >= settings.cow_start_day
        and cows_placed + cows_owned < settings.cow_max
        and money - reserve >= _num(ANIMALS["COW"]["cost"])
        and len(orders) < cap
    ):
        orders.append(["BUY_ANIMAL", "COW", 1])
        money -= _num(ANIMALS["COW"]["cost"])
    geese_placed = _count_animal(snapshot, "GOOSE")
    geese_owned = _int(snapshot.shed().get("GOOSE"), 0)
    if (
        snapshot.day >= settings.cow_start_day + 2
        and geese_placed + geese_owned < settings.goose_max
        and money - reserve >= _num(ANIMALS["GOOSE"]["cost"])
        and len(orders) < cap
    ):
        orders.append(["BUY_ANIMAL", "GOOSE", 1])
        money -= _num(ANIMALS["GOOSE"]["cost"])


def _count_animal(snapshot: GameSnapshot, animal: str) -> int:
    n = 0
    for y in range(snapshot.board_size):
        for x in range(snapshot.board_size):
            tile = snapshot.tile_at(x, y)
            if isinstance(tile, dict) and tile.get("animal") == animal:
                n += 1
    return n
