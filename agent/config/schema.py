"""Configuration schema: canonical defaults for every configurable value.

The schema is the single source of truth for default values.  Production code
must never hard-code configuration; instead it reads from the ``Settings``
object produced by :func:`agent.config.loader.load_config`, which merges
sources on top of the defaults declared here.

Priority (highest first):
    1. Command-line overrides
    2. Environment variables
    3. YAML configuration file
    4. Schema defaults (this module)
"""
from __future__ import annotations

from typing import Any

ENV_PREFIX = "KAG_"

DEFAULTS: dict[str, Any] = {
    "environment": "development",
    "seed": None,
    "game": {
        "episode_steps": 720,
        "turns_per_day": 24,
        "board_size": 10,
        "starting_money": 3000,
        "farm_hand_cost_mult": 1,
        "shed_capacity": 100,
        "weed_spawn_chance": 0.005,
    },
    "market": {
        "max_market_orders_per_turn": 10,
        "floor_price": 1,
        "base_prices": {
            "WHEAT": 10,
            "CARROT": 20,
            "TOMATO": 30,
            "STRAWBERRY": 50,
            "MELON": 80,
            "GOOSE": 30,
            "COW": 50,
            "SHEEP": 40,
            "FERTILIZER": 15,
        },
        "price_shapes": {
            "WHEAT": {"below": "linear", "above": "linear"},
            "CARROT": {"below": "linear", "above": "sq"},
            "TOMATO": {"below": "sqrt", "above": "sq"},
            "STRAWBERRY": {"below": "log", "above": "sqrt"},
            "MELON": {"below": "log", "above": "sqrt"},
            "GOOSE": {"below": "linear", "above": "sqrt"},
            "COW": {"below": "linear", "above": "sqrt"},
            "SHEEP": {"below": "linear", "above": "sqrt"},
            "FERTILIZER": {"below": "linear", "above": "linear"},
        },
        "initial_inventory": {
            "WHEAT": 20,
            "CARROT": 15,
            "TOMATO": 15,
            "STRAWBERRY": 10,
            "MELON": 5,
            "GOOSE": 5,
            "COW": 3,
            "SHEEP": 3,
            "FERTILIZER": 10,
        },
    },
    "town": {
        "town_center_sell_interval": 12,
        "town_shop_unlock_interval": 3,
        "town_shop_sell_interval": 4,
    },
    "strategy": {
        "name": "baseline",
        "version": "1.0.0",
        "max_candidates": 50,
        "evaluation_timeout_ms": 50,
        "planning": {"horizon_days": 5, "max_tasks_per_day": 20},
        "crops": {
            "prioritize_high_value": True,
            "watering_bonus_window": True,
            "fertilizer_threshold": 0.3,
        },
        "animals": {
            "feed_priority": "high",
            "care_bonus": True,
            "collect_fertilizer": True,
        },
        "market": {
            "sell_threshold": 0.8,
            "buy_threshold": 0.2,
            "price_lookback": 10,
        },
        "economy": {
            "min_cash_reserve": 500,
            "land_buy_order": ["NW", "NE", "SW", "SE"],
            "land_costs": {"NE": 1000, "SW": 2000, "SE": 4000},
        },
    },
    "features": {
        "ENABLE_PROFILING": False,
        "ENABLE_TRACE": True,
        "ENABLE_METRICS": True,
        "ENABLE_DEBUG_LOGGING": False,
        "ENABLE_DECISION_REPLAY": True,
        "ENABLE_PERFORMANCE_CACHE": True,
    },
    "performance": {
        "observation_parsing_ms": 5,
        "decision_engine_ms": 20,
        "strategy_evaluation_ms": 10,
        "action_conversion_ms": 2,
        "total_decision_ms": 500,
        "warning_threshold_ms": 800,
        "failure_threshold_ms": 1500,
        "memory_per_step_mb": 10,
        "peak_memory_mb": 100,
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/app.log",
        "structured": True,
    },
    "observability": {
        "metrics_enabled": True,
        "tracers": ["memory"],
        "replay_enabled": True,
        "replay_directory": "replays",
        "export_enabled": False,
    },
    "simulation": {
        "num_episodes": 100,
        "opponent": "random",
        "replay": {
            "enabled": True,
            "directory": "replays/",
        },
        "metrics": [
            "reward",
            "coins",
            "crops_harvested",
            "animals_produced",
            "market_orders",
            "decision_latency_ms",
        ],
    },
}

VALID_ENVS = {"development", "staging", "production"}
VALID_STRATEGIES = {"baseline", "heuristic", "economic", "utility"}
VALID_PRICE_SHAPES = {"linear", "sq", "sqrt", "log"}
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into ``base`` returning a new dict."""
    result: dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, dict):
            sub = override.get(key, {})
            if isinstance(sub, dict):
                result[key] = deep_merge(value, sub)
            else:
                result[key] = sub
        else:
            result[key] = override.get(key, value)
    for key, value in override.items():
        if key not in result:
            result[key] = value
    return result


def schema_defaults() -> dict[str, Any]:
    """Return a fresh deep copy of the schema defaults."""
    import copy

    return copy.deepcopy(DEFAULTS)
