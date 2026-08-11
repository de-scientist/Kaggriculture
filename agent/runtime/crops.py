"""Crop selection and per-crop economics for the champion planner."""

from __future__ import annotations

from typing import Mapping

from .constants import CROPS, MARKET, window_end_day, window_start_day
from .game import GameSnapshot, count_plants_by_crop
from .settings import RuntimeSettings

# Planned yield for a one-time crop assuming the watering bonus window is
# serviced (watered every day from window_start to window_end).
_WINDOW_YIELD = {
    "WHEAT": 1 + (window_end_day("WHEAT") - window_start_day("WHEAT") + 1),
    "CARROT": 1 + (window_end_day("CARROT") - window_start_day("CARROT") + 1),
    "MELON": 1 + (window_end_day("MELON") - window_start_day("MELON") + 1),
}

_ONGOING_YIELD = {
    "TOMATO": int(CROPS["TOMATO"]["max_yield"]),
    "STRAWBERRY": int(CROPS["STRAWBERRY"]["max_yield"]),
}

# Rough days a tile is committed when a crop is planted today.
_CYCLE_DAYS = {
    "WHEAT": 5,
    "CARROT": 4,
    "TOMATO": 13,
    "STRAWBERRY": 17,
    "MELON": 13,
}

# Multipliers applied to the *current* market price when estimating what we can
# actually realize, reflecting per-product glut sensitivity.
_PRICE_REALIZATION = {
    "WHEAT": 1.0,
    "CARROT": 0.95,
    "TOMATO": 0.9,
    "STRAWBERRY": 0.9,
    "MELON": 0.85,
}


def expected_yield(crop: str) -> int:
    if bool(CROPS[crop]["ongoing"]):
        return _ONGOING_YIELD.get(crop, 0)
    return min(int(CROPS[crop]["max_yield"]), _WINDOW_YIELD.get(crop, 1))


def cycle_days(crop: str) -> int:
    return _CYCLE_DAYS.get(crop, 5)


def crop_daily_value(crop: str, prices: Mapping[str, object], day: int) -> float:
    """Estimated net coins per day per tile for planting ``crop`` today."""
    cd = CROPS[crop]
    base = int(MARKET[crop]["base"])
    raw = prices.get(crop, base)
    try:
        current = float(raw)
    except (TypeError, ValueError):
        current = float(base)
    realized = current * _PRICE_REALIZATION.get(crop, 0.9)
    yield_units = expected_yield(crop)
    profit = yield_units * realized - int(cd["seed"])
    cyc = cycle_days(crop)
    if cyc <= 0:
        return 0.0
    return profit / cyc


def can_mature(crop: str, day: int) -> bool:
    """True if planting ``crop`` on ``day`` still yields before season end."""
    cd = CROPS[crop]
    first = int(cd["first_yield_day"])
    if bool(cd["ongoing"]):
        productions = (29 - day - first + int(cd["interval"])) // int(cd["interval"])
        return productions >= 1
    return day + int(cd["max_yield_day"]) <= 29


def best_crop(snapshot: GameSnapshot, settings: RuntimeSettings) -> str:
    """Pick the crop the champion should plant on free tiles this turn."""
    day = snapshot.day
    money = snapshot.money()
    remaining = 29 - day

    if remaining < 3:
        return "WHEAT"
    if remaining < 6:
        return "CARROT"
    if remaining < 10:
        return "CARROT"
    if day < settings.melon_start_day:
        # Early cash-building phase: quick, price-stable carrots.
        return "CARROT"

    # Melon is only worth the price-crash risk when the opponent is not
    # flooding the market with melons too, and once we have enough capital to
    # leave tiles idle for 13 days.
    opp_melons = count_plants_by_crop(snapshot.opp(), "MELON")
    my_melons = count_plants_by_crop(snapshot.me(), "MELON")
    if (
        day >= settings.melon_start_day
        and opp_melons < settings.melon_opp_gate
        and my_melons < settings.melon_max_tiles
        and money >= settings.reserve_money + int(CROPS["MELON"]["seed"])
    ):
        return "MELON"
    return "WHEAT"


def melon_tiles_allowed(snapshot: GameSnapshot, settings: RuntimeSettings) -> int:
    """Upper bound on MELON tiles, shrinking as the opponent plants melons."""
    opp_melons = count_plants_by_crop(snapshot.opp(), "MELON")
    return max(0, settings.melon_max_tiles - max(0, opp_melons - settings.melon_opp_gate + 1))
