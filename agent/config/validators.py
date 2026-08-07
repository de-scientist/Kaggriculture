"""Configuration validation: fail fast on invalid configuration.

Validators enforce invariants on the merged configuration so that invalid
values never reach runtime.  Any validation failure raises
:class:`~agent.exceptions.configuration.ConfigurationError` with a message
identifying the offending key.
"""
from __future__ import annotations

from typing import Any

from agent.exceptions.configuration import ConfigurationError

from .schema import (
    VALID_ENVS,
    VALID_LOG_LEVELS,
    VALID_PRICE_SHAPES,
    VALID_STRATEGIES,
)


class ConfigValidator:
    """Validates a merged configuration mapping."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._errors: list[str] = []

    def validate(self) -> None:
        self._validate_environment()
        self._validate_game()
        self._validate_market()
        self._validate_town()
        self._validate_strategy()
        self._validate_features()
        self._validate_performance()
        self._validate_logging()
        self._validate_observability()
        if self._errors:
            raise ConfigurationError(
                "Invalid configuration:\n  - " + "\n  - ".join(self._errors)
            )

    # -- helpers -------------------------------------------------------------
    def _game(self) -> dict[str, Any]:
        return self._config.get("game", {})

    def _market(self) -> dict[str, Any]:
        return self._config.get("market", {})

    def _strategy(self) -> dict[str, Any]:
        return self._config.get("strategy", {})

    def _features(self) -> dict[str, Any]:
        return self._config.get("features", {})

    def _performance(self) -> dict[str, Any]:
        return self._config.get("performance", {})

    def _logging(self) -> dict[str, Any]:
        return self._config.get("logging", {})

    def _observability(self) -> dict[str, Any]:
        return self._config.get("observability", {})

    # -- individual validators ----------------------------------------------
    def _validate_environment(self) -> None:
        env = self._config.get("environment")
        if env is not None and env not in VALID_ENVS:
            self._errors.append(f"environment '{env}' is not valid; use one of {sorted(VALID_ENVS)}")

    def _validate_game(self) -> None:
        game = self._game()
        self._check_positive_int(game, "episode_steps")
        self._check_positive_int(game, "turns_per_day")
        self._check_positive_int(game, "board_size")
        self._check_positive_number(game, "starting_money")
        self._check_positive_number(game, "farm_hand_cost_mult")
        self._check_positive_int(game, "shed_capacity")
        self._check_range(game, "weed_spawn_chance", 0.0, 1.0)

    def _validate_market(self) -> None:
        market = self._market()
        self._check_positive_int(market, "max_market_orders_per_turn")
        self._check_positive_int(market, "floor_price")
        for shape_name, shape in market.get("price_shapes", {}).items():
            for side in ("below", "above"):
                value = shape.get(side)
                if value is not None and value not in VALID_PRICE_SHAPES:
                    self._errors.append(
                        f"market.price_shapes.{shape_name}.{side}='{value}' is not a "
                        f"valid shape; use one of {sorted(VALID_PRICE_SHAPES)}"
                    )

    def _validate_town(self) -> None:
        town = self._config.get("town", {})
        self._check_positive_int(town, "town_center_sell_interval")
        self._check_positive_int(town, "town_shop_unlock_interval")
        self._check_positive_int(town, "town_shop_sell_interval")

    def _validate_strategy(self) -> None:
        strategy = self._strategy()
        name = strategy.get("name")
        if name is not None and name not in VALID_STRATEGIES:
            self._errors.append(
                f"strategy.name '{name}' is not registered; use one of {sorted(VALID_STRATEGIES)}"
            )
        self._check_positive_int(strategy, "max_candidates")
        self._check_positive_number(strategy, "evaluation_timeout_ms")
        economy = strategy.get("economy", {})
        self._check_positive_number(economy, "min_cash_reserve")

    def _validate_features(self) -> None:
        for flag in self._features():
            if not flag.startswith("ENABLE_"):
                self._errors.append(
                    f"feature flag '{flag}' must start with ENABLE_"
                )

    def _validate_performance(self) -> None:
        perf = self._performance()
        for key in (
            "observation_parsing_ms",
            "decision_engine_ms",
            "strategy_evaluation_ms",
            "action_conversion_ms",
            "total_decision_ms",
        ):
            self._check_positive_number(perf, key)
        for key in ("warning_threshold_ms", "failure_threshold_ms"):
            self._check_positive_number(perf, key)
        self._check_order(perf, "total_decision_ms", "warning_threshold_ms")
        self._check_order(perf, "warning_threshold_ms", "failure_threshold_ms")

    def _validate_logging(self) -> None:
        log = self._logging()
        level = log.get("level")
        if level is not None and level not in VALID_LOG_LEVELS:
            self._errors.append(
                f"logging.level '{level}' is not valid; use one of {sorted(VALID_LOG_LEVELS)}"
            )

    def _validate_observability(self) -> None:
        obs = self._observability()
        self._check_bool(obs, "metrics_enabled")
        self._check_bool(obs, "tracers")
        self._check_bool(obs, "replay_enabled")

    # -- generic numerical checks -------------------------------------------
    def _check_positive_int(self, mapping: dict[str, Any], key: str) -> None:
        value = mapping.get(key)
        if value is None:
            return
        if not isinstance(value, int) or isinstance(value, bool):
            self._errors.append(f"{key} must be an integer, got {type(value).__name__} ({value!r})")
        elif value <= 0:
            self._errors.append(f"{key} must be positive, got {value}")

    def _check_positive_number(self, mapping: dict[str, Any], key: str) -> None:
        value = mapping.get(key)
        if value is None:
            return
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            self._errors.append(f"{key} must be a number, got {type(value).__name__} ({value!r})")
        elif value <= 0:
            self._errors.append(f"{key} must be positive, got {value}")

    def _check_range(self, mapping: dict[str, Any], key: str, low: float, high: float) -> None:
        value = mapping.get(key)
        if value is None:
            return
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            self._errors.append(f"{key} must be a number, got {value!r}")
        elif not (low <= value <= high):
            self._errors.append(f"{key} must be between {low} and {high}, got {value}")

    def _check_bool(self, mapping: dict[str, Any], key: str) -> None:
        value = mapping.get(key)
        if value is None:
            return
        if not isinstance(value, (bool, str)):
            self._errors.append(f"{key} must be a boolean or list, got {value!r}")

    def _check_order(self, mapping: dict[str, Any], a: str, b: str) -> None:
        va, vb = mapping.get(a), mapping.get(b)
        if va is None or vb is None:
            return
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            if va > vb:
                self._errors.append(f"{a} ({va}) must be <= {b} ({vb})")


def validate_settings(config: dict[str, Any]) -> None:
    """Validate a merged configuration mapping.

    Raises :class:`ConfigurationError` if any value is invalid.
    """
    ConfigValidator(config).validate()
