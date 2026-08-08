"""Tests for the configuration layer (schema, loader, settings, validators)."""
from __future__ import annotations

import pytest

from agent.config import (
    Settings,
    deep_merge,
    get_config,
    load_config,
    reset_config,
    schema_defaults,
    validate_settings,
)
from agent.exceptions.configuration import ConfigurationError


def test_schema_defaults_contains_canonical_sections() -> None:
    defaults = schema_defaults()
    for key in ("environment", "seed", "game", "market", "town", "strategy",
                "features", "performance", "logging", "observability", "simulation"):
        assert key in defaults
    assert defaults["game"]["episode_steps"] == 720
    assert defaults["game"]["starting_money"] == 3000
    assert defaults["strategy"]["name"] == "baseline"


def test_schema_defaults_is_a_fresh_copy() -> None:
    a = schema_defaults()
    b = schema_defaults()
    a["game"]["episode_steps"] = 999
    assert b["game"]["episode_steps"] == 720


def test_deep_merge_overrides_scalar_and_merges_nested() -> None:
    base = {"a": 1, "nested": {"x": 1, "y": 2}}
    override = {"b": 2, "nested": {"y": 20, "z": 3}}
    merged = deep_merge(base, override)
    assert merged == {"a": 1, "b": 2, "nested": {"x": 1, "y": 20, "z": 3}}
    # originals unchanged
    assert base == {"a": 1, "nested": {"x": 1, "y": 2}}
    assert override == {"b": 2, "nested": {"y": 20, "z": 3}}


def test_deep_merge_non_dict_override_replaces() -> None:
    merged = deep_merge({"a": {"b": 1}}, {"a": "replaced"})
    assert merged == {"a": "replaced"}


def test_load_config_development_defaults() -> None:
    settings = load_config("development")
    assert isinstance(settings, Settings)
    assert settings.environment == "development"
    assert settings.seed == 42
    assert settings.game["episode_steps"] == 720
    assert settings.strategy_name == "baseline"
    assert settings.log_level == "DEBUG"


def test_get_config_caches_instance() -> None:
    reset_config()
    first = get_config("development")
    second = get_config("development")
    assert first is second


def test_get_config_reload_forces_refresh() -> None:
    reset_config()
    first = get_config("development")
    second = get_config("development", reload=True)
    assert first is not second
    assert second.seed == 42


def test_environment_variable_overrides_strategy_name() -> None:
    settings = load_config(
        "development", env={"KAG_STRATEGY__NAME": "utility"}
    )
    assert settings.strategy_name == "utility"
    assert settings.get("strategy", {}).get("name") == "utility"


def test_environment_variable_overrides_nested_logging_level() -> None:
    settings = load_config(
        "development", env={"KAG_LOGGING__LEVEL": "ERROR"}
    )
    assert settings.log_level == "ERROR"


def test_cli_dotted_overrides_win() -> None:
    settings = load_config(
        "development", overrides={"strategy.name": "heuristic", "seed": 7}
    )
    assert settings.strategy_name == "heuristic"
    assert settings.seed == 7


def test_cli_override_wins_over_env() -> None:
    settings = load_config(
        "development",
        env={"KAG_STRATEGY__NAME": "utility"},
        overrides={"strategy.name": "economic"},
    )
    assert settings.strategy_name == "economic"


def test_env_coerces_types() -> None:
    settings = load_config(
        "development",
        env={
            "KAG_GAME__BOARD_SIZE": "15",
            "KAG_OBSERVABILITY__METRICS_ENABLED": "true",
        },
    )
    assert settings.game["board_size"] == 15
    assert settings.observability["metrics_enabled"] is True


def test_settings_is_frozen_and_immutable() -> None:
    reset_config()
    settings = load_config("development")
    with pytest.raises(Exception):
        settings.strategy_name = "other"  # type: ignore[misc]


def test_settings_dict_style_access() -> None:
    reset_config()
    settings = load_config("development")
    assert settings.get("strategy")["name"] == "baseline"
    assert settings["environment"] == "development"
    assert "seed" in settings
    with pytest.raises(KeyError):
        _ = settings["nonexistent_key"]


def test_settings_feature_flag_accessors() -> None:
    settings = load_config("development")
    flags = settings.feature_flags
    assert flags["ENABLE_TRACE"] is True
    assert settings.is_feature_enabled("ENABLE_TRACE") is True
    assert settings.is_feature_enabled("ENABLE_PROFILING") is False


def test_settings_performance_budgets_accessor() -> None:
    settings = load_config("development")
    budgets = settings.performance_budgets
    assert budgets["total_decision_ms"] == 500
    assert budgets["observation_parsing_ms"] == 5


def test_invalid_environment_raises() -> None:
    with pytest.raises(ConfigurationError):
        load_config("development", env={"KAG_ENVIRONMENT": "qa"})


def test_invalid_strategy_name_raises() -> None:
    with pytest.raises(ConfigurationError):
        load_config("development", env={"KAG_STRATEGY__NAME": "nonexistent"})


def test_invalid_log_level_raises() -> None:
    with pytest.raises(ConfigurationError):
        load_config("development", env={"KAG_LOGGING__LEVEL": "VERBOSE"})


def test_validate_settings_rejects_bad_config() -> None:
    bad = schema_defaults()
    bad["game"]["board_size"] = -1
    bad["environment"] = "qa"
    with pytest.raises(ConfigurationError):
        validate_settings(bad)


def test_validate_settings_accepts_defaults() -> None:
    validate_settings(schema_defaults())


def test_config_validator_collects_multiple_errors() -> None:
    bad = schema_defaults()
    bad["environment"] = "qa"
    bad["game"]["board_size"] = -5
    with pytest.raises(ConfigurationError) as exc:
        validate_settings(bad)
    msg = str(exc.value)
    assert "environment 'qa'" in msg
    assert "board_size must be positive" in msg
