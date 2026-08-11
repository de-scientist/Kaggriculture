"""Runtime planner settings.

Values are conservative defaults tuned by benchmark; a handful can be
overridden through ``KAG_RUNTIME_*`` environment variables so experiments do
not require code edits.  The learning layer may adjust a subset of these knobs
(see :mod:`agent.runtime.policies`).
"""

from __future__ import annotations

import os
import dataclasses
from dataclasses import dataclass, fields
from typing import Any


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class RuntimeSettings:
    """Knobs for the champion planner and the hybrid policy."""

    reserve_money: float = 200.0
    max_market_orders: int = 10
    shed_high_watermark: float = 0.85

    # Hands are re-hired at the start of every day; cost is the cheap fib series.
    target_hands: tuple[int, ...] = (3, 4, 5, 6)
    hand_phase_days: tuple[int, ...] = (0, 4, 12, 22)

    # Crop planning.
    melon_start_day: int = 6
    melon_max_tiles: int = 8
    melon_opp_gate: int = 3
    melon_sell_cap: int = 3
    sell_min_ratio: float = 0.85
    wheat_keep_buffer: int = 5
    endgame_sell_day: int = 26
    carrot_switch_day: int = 18
    wheat_switch_day: int = 21

    # Land expansion: buy quadrant when money >= cost * ratio and day < latest.
    land_budget_ratio: float = 2.0
    land_latest_day: tuple[int, int, int] = (22, 16, 10)

    # Animals (opt-in; the module is only active when enable_animals is true).
    enable_animals: bool = False
    cow_max: int = 2
    goose_max: int = 1
    cow_start_day: int = 4
    cow_min_money: float = 2600.0
    cow_max_wheat_ratio: float = 1.25
    animal_wheat_buffer: int = 12

    # Experience recording + learning.
    record_experience: bool = False
    experience_dir: str = "replays"
    max_market_buy_seed_units: int = 12

    @classmethod
    def from_env(cls, overrides: dict[str, Any] | None = None) -> "RuntimeSettings":
        merged: dict[str, Any] = {}
        if overrides:
            merged.update(overrides)
        for f in fields(cls):
            default = f.default
            if default is dataclasses.MISSING:  # type: ignore[name-defined]
                continue
            env_value: Any = None
            env_key = "KAG_RUNTIME_" + f.name.upper()
            if isinstance(default, bool):
                env_raw = os.environ.get(env_key)
                if env_raw is not None:
                    env_value = env_raw.strip().lower() in ("1", "true", "yes", "on")
            elif isinstance(default, int):
                env_value = _env_int(env_key, default)
            elif isinstance(default, float):
                env_value = _env_float(env_key, default)
            if env_value is not None:
                merged[f.name] = env_value
        return cls(**merged)
