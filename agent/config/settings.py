"""Immutable application settings.

``Settings`` is the canonical, immutable view of configuration consumed by
all production code.  It is built once at start-up by the configuration loader
from merged sources (defaults -> YAML -> environment -> CLI overrides) and
validated before use.

The object supports both attribute (``settings.game``) and dict-style
(``settings.get("strategy")``) access so that legacy call-sites that treat
the config as a mapping keep working.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any


@dataclass(frozen=True)
class Settings:
    environment: str = "development"
    seed: int | None = None
    game: dict[str, Any] = field(default_factory=lambda: {
        "episode_steps": 720,
        "turns_per_day": 24,
        "board_size": 10,
        "starting_money": 3000,
        "farm_hand_cost_mult": 1,
        "shed_capacity": 100,
        "weed_spawn_chance": 0.005,
    })
    market: dict[str, Any] = field(default_factory=lambda: {
        "max_market_orders_per_turn": 10,
        "floor_price": 1,
    })
    town: dict[str, Any] = field(default_factory=dict)
    logging: dict[str, Any] = field(default_factory=dict)
    strategy: dict[str, Any] = field(default_factory=dict)
    features: dict[str, Any] = field(default_factory=dict)
    performance: dict[str, Any] = field(default_factory=dict)
    observability: dict[str, Any] = field(default_factory=dict)
    simulation: dict[str, Any] = field(default_factory=dict)

    # -- dict-style access (for backward compat) --------------------------
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __contains__(self, key: str) -> object:
        return hasattr(self, key)

    # -- serialisation ----------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for f in fields(self):
            result[f.name] = getattr(self, f.name)
        return result

    def keys(self) -> list[str]:
        return [f.name for f in fields(self)]

    # -- typed accessors --------------------------------------------------
    @property
    def feature_flags(self) -> dict[str, bool]:
        return dict(self.features)

    def is_feature_enabled(self, flag: str) -> bool:
        return bool(self.features.get(flag, False))

    @property
    def performance_budgets(self) -> dict[str, int | float]:
        return dict(self.performance)

    @property
    def observability_config(self) -> dict[str, Any]:
        return dict(self.observability)

    @property
    def strategy_name(self) -> str:
        return str(self.strategy.get("name", "baseline"))

    @property
    def log_level(self) -> str:
        return str(self.logging.get("level", "INFO")).upper()
