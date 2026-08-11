"""Versioned feature engineering for the learning layer.

``build_features(snapshot)`` turns one fully-observable :class:`GameSnapshot`
into a fixed-length list of floats used to train and run the Stage 3 models.
The vector contains only information the observation exposes at that turn:

* no future information (nothing from turn > t),
* no opponent private state (shed / seeds / inventories),
* no engine internals.

The feature definition is versioned via :data:`FEATURE_VERSION`.  Models are
refused at load time when their feature version differs from the current one.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from ..runtime.constants import CROPS, MARKET
from ..runtime.game import GameSnapshot, count_plants_by_crop
from .schema import CROPS as _FEATURE_CROPS
from .schema import SALEABLE_PRODUCTS as _FEATURE_PRODUCTS

# Keep the schema import used for the canonical order.
FEATURE_CROPS = _FEATURE_CROPS
FEATURE_PRODUCTS = _FEATURE_PRODUCTS

FEATURE_VERSION = 1

_PRODUCTS = FEATURE_PRODUCTS
_CROPS = FEATURE_CROPS

# Stable, human-readable feature names.  Order MUST match build_features.
FEATURE_NAMES: list[str] = [
    # -- season (3) --
    "day_norm",
    "hour_norm",
    "remaining_days_norm",
    # -- wealth (6) --
    "money_norm",
    "money_log1p",
    "opp_money_norm",
    "money_diff_norm",
    "shed_value_norm",
    "shed_occupancy_norm",
    "farmer_inv_value_norm",
    # -- shed counts (9 products) --
    *[f"shed_{p.lower()}" for p in _PRODUCTS],
    "shed_fertilizer",
    # -- seeds (5) --
    *[f"seeds_{c.lower()}" for c in _CROPS],
    # -- my plants (5) --
    *[f"plants_{c.lower()}" for c in _CROPS],
    # -- opponent plants (5) --
    *[f"opp_plants_{c.lower()}" for c in _CROPS],
    # -- land / workers (4) --
    "unlocked_norm",
    "opp_unlocked_norm",
    "hands_norm",
    "opp_hands_norm",
    # -- activity (3) --
    "weed_norm",
    "empty_tiles_norm",
    "plants_total_norm",
    # -- market price ratios (8) --
    *[f"price_{p.lower()}_ratio" for p in _PRODUCTS],
    # -- market inventory log (8) --
    *[f"inv_{p.lower()}_log" for p in _PRODUCTS],
    # -- town (1) --
    "shops_norm",
]

NUM_FEATURES = len(FEATURE_NAMES)


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


def compact_state(snapshot: GameSnapshot) -> dict[str, Any]:
    """Deterministic, JSON-safe extraction of everything the features need.

    Stored with every experience so the feature vector can be rebuilt when the
    feature definition changes without re-running games.
    """
    shed = {str(k): _int(v) for k, v in snapshot.shed().items()}
    seeds = {str(k): _int(v) for k, v in snapshot.seeds().items()}
    prices = {str(k): _num(v) for k, v in snapshot.prices().items()}
    market_inv = {str(k): _num(v) for k, v in snapshot.market_inventory().items()}

    opp = snapshot.opp()
    opp_unlocked = opp.get("unlocked_quadrants", [])
    opp_hands = opp.get("hands", [])
    return {
        "day": snapshot.day,
        "hour": snapshot.hour,
        "remaining_days": snapshot.remaining_days(),
        "money": snapshot.money(),
        "opp_money": snapshot.opp_money(),
        "shed": shed,
        "seeds": seeds,
        "shed_occupancy": snapshot.shed_occupancy(),
        "shed_value": snapshot.shed_value(),
        "farmer_inv_value": snapshot.inventory_value(0),
        "plants": {c: count_plants_by_crop(snapshot.me(), c) for c in CROPS},
        "opp_plants": {c: count_plants_by_crop(snapshot.opp(), c) for c in CROPS},
        "unlocked": snapshot.unlocked_count(),
        "opp_unlocked": len(opp_unlocked),
        "hands": len(snapshot.hands()),
        "opp_hands": len(opp_hands),
        "weed_count": len(snapshot.weed_tiles()),
        "empty_tiles": len(snapshot.empty_tiles()),
        "prices": prices,
        "market_inventory": market_inv,
        "shops": len(snapshot.shops()),
        "board_size": snapshot.board_size,
        "turns_per_day": snapshot.turns_per_day,
        "episode_steps": snapshot.episode_steps,
    }


def build_features(snapshot: GameSnapshot) -> list[float]:
    """Fixed-length feature vector for one snapshot (no future information)."""
    return build_features_from_state(compact_state(snapshot))


def build_features_from_state(state: Mapping[str, Any]) -> list[float]:
    """Feature vector computed from a :func:`compact_state` dict."""
    steps_per_day = max(1, _int(state.get("turns_per_day"), 24))
    season_days = max(1, _int(state.get("episode_steps"), 720) // steps_per_day)
    day = _int(state.get("day"), 0)
    hour = _int(state.get("hour"), 0)
    remaining = max(0, _int(state.get("remaining_days"), 0))

    money = _num(state.get("money"))
    opp_money = _num(state.get("opp_money"))
    shed = state.get("shed", {}) if isinstance(state.get("shed"), Mapping) else {}
    seeds = state.get("seeds", {}) if isinstance(state.get("seeds"), Mapping) else {}
    plants = state.get("plants", {}) if isinstance(state.get("plants"), Mapping) else {}
    opp_plants = state.get("opp_plants", {}) if isinstance(state.get("opp_plants"), Mapping) else {}
    prices = state.get("prices", {}) if isinstance(state.get("prices"), Mapping) else {}
    market_inv = (
        state.get("market_inventory", {})
        if isinstance(state.get("market_inventory"), Mapping)
        else {}
    )

    f: list[float] = [
        day / max(1, season_days),
        hour / max(1, _int(state.get("turns_per_day"), 24)),
        remaining / max(1, season_days),
        money / 1000.0,
        math.log1p(max(0.0, money)),
        opp_money / 1000.0,
        (money - opp_money) / 1000.0,
        _num(state.get("shed_value")) / 1000.0,
        _int(state.get("shed_occupancy")) / 100.0,
        _num(state.get("farmer_inv_value")) / 1000.0,
    ]

    for product in _PRODUCTS:
        f.append(_int(shed.get(product)) / 20.0)
    f.append(_int(shed.get("FERTILIZER")) / 20.0)

    for crop in _CROPS:
        f.append(_int(seeds.get(crop)) / 20.0)
    for crop in _CROPS:
        f.append(_int(plants.get(crop)) / 25.0)
    for crop in _CROPS:
        f.append(_int(opp_plants.get(crop)) / 25.0)

    f.append(_int(state.get("unlocked")) / 4.0)
    f.append(_int(state.get("opp_unlocked")) / 4.0)
    f.append(_int(state.get("hands")) / 6.0)
    f.append(_int(state.get("opp_hands")) / 6.0)

    f.append(_int(state.get("weed_count")) / 25.0)
    f.append(_int(state.get("empty_tiles")) / 100.0)
    total_plants = sum(_int(plants.get(c)) for c in _CROPS)
    f.append(total_plants / 100.0)

    for product in _PRODUCTS:
        base = int(MARKET[product]["base"])
        price = _num(prices.get(product), base)
        f.append((price - base) / base)
    for product in _PRODUCTS:
        f.append(math.log1p(max(0.0, _num(market_inv.get(product)))) / math.log1p(10000.0))

    f.append(_int(state.get("shops")) / 8.0)

    if len(f) != NUM_FEATURES:
        raise ValueError(f"feature count mismatch: expected {NUM_FEATURES}, got {len(f)}")
    return f
