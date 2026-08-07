"""Configuration loader with multi-source merging.

Sources are merged in priority order (highest last so it wins):

    1. Schema defaults       (``agent/config/schema.py``)
    2. YAML file             (``configs/<name>.yaml``)
    3. Environment variables ``KAG_*``
    4. Command-line overrides (dict passed to :func:`load_config`)

The resulting :class:`Settings` is immutable and validated before being
returned.  Invalid configuration raises ``ConfigurationError`` immediately
(fail fast).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from agent.exceptions.configuration import ConfigurationError

from .schema import DEFAULTS, deep_merge, schema_defaults
from .settings import Settings
from .validators import validate_settings

DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"

_ENV_DELIMITER = "."


def load_config(
    name: str = "development",
    *,
    overrides: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> Settings:
    """Load, merge, and validate configuration.

    Args:
        name: Base YAML config file name (without ``.yaml``).
        overrides: Highest-priority key/value overrides (e.g. CLI flags).
            Supports dotted keys for nested override, e.g. ``{"strategy.name": "utility"}``.
        env: Environment mapping.  Defaults to ``os.environ``.

    Returns:
        Immutable, validated :class:`Settings`.

    Raises:
        ConfigurationError: If the file is missing or values are invalid.
    """
    merged = schema_defaults()

    yaml_data = _load_yaml(name)
    merged = deep_merge(merged, yaml_data)

    env_data = _load_environment(env if env is not None else os.environ)
    merged = deep_merge(merged, env_data)

    if overrides:
        merged = deep_merge(merged, _flatten_overrides(overrides))

    validate_settings(merged)
    return Settings(**merged)


def _load_yaml(name: str) -> dict[str, Any]:
    path = DEFAULT_CONFIG_DIR / f"{name}.yaml"
    if name != "development" and not path.exists():
        return {}
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ConfigurationError(
            f"Config file {path} must contain a top-level mapping, got {type(data).__name__}"
        )
    return data


def _load_environment(env: Mapping[str, str]) -> dict[str, Any]:
    prefix = "KAG_"
    values = env.get("KAG_ENVIRONMENT")
    result: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.startswith(prefix):
            continue
        stripped = key[len(prefix):]
        if not stripped:
            continue
        result = deep_merge(result, _set_path(result, stripped, _coerce(raw)))
    return result


def _coerce(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "none"):
        return None
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def _set_path(base: dict[str, Any], dotted: str, value: Any) -> dict[str, Any]:
    node = base
    parts = [p.lower() for p in dotted.split("__")]
    for part in parts[:-1]:
        if part not in node or not isinstance(node.get(part), dict):
            node[part] = {}
        node = node[part]
    node[parts[-1]] = value
    return base


def _flatten_overrides(overrides: Mapping[str, Any]) -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in overrides.items():
        if "." in key:
            node = flat
            parts = key.split(".")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = value
        else:
            flat[key] = value
    return flat


_cached: Settings | None = None


def get_config(name: str = "development", *, reload: bool = False) -> Settings:
    """Return the cached :class:`Settings`, loading it if necessary.

    Pass ``reload=True`` to force a fresh load (useful when environment has
    changed during a test).
    """
    global _cached
    if _cached is None or reload:
        _cached = load_config(name)
    return _cached


def reset_config() -> None:
    """Drop the cached settings (primarily for testing)."""
    global _cached
    _cached = None
