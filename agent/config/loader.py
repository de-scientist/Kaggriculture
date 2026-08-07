"""Configuration loader with multi-source merging.

The effective configuration is built from several layers, merged in priority
order (highest last so it wins):

    1. Schema defaults        (``agent/config/schema.py``)
    2. Domain YAML files       (``configs/strategy.yaml``, ``logging.yaml`` …)
    3. Environment YAML file   (``configs/<env>.yaml``)
    4. Environment variables   ``KAG_*``
    5. Command-line overrides  (dict passed to :func:`load_config`)

The resulting :class:`Settings` is immutable and validated before being
returned.  Invalid configuration raises ``ConfigurationError`` immediately
(fail fast).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

import yaml

from agent.exceptions.configuration import ConfigurationError

from .schema import deep_merge, schema_defaults
from .settings import Settings
from .validators import validate_settings

DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"

# Domain files merged first (lowest priority after defaults), in load order.
DOMAIN_FILES = ("market", "logging", "performance", "features", "strategy", "simulation")

_ENV_PREFIX = "KAG_"


def load_config(
    name: str = "development",
    *,
    overrides: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> Settings:
    """Load, merge, and validate configuration.

    Args:
        name: Environment YAML config file name (without ``.yaml``).
        overrides: Highest-priority key/value overrides (e.g. CLI flags).
            Supports dotted keys for nested override, e.g.
            ``{"strategy.name": "utility"}``.
        env: Environment mapping.  Defaults to ``os.environ``.

    Returns:
        Immutable, validated :class:`Settings`.

    Raises:
        ConfigurationError: If a required file is missing or values are invalid.
    """
    merged = schema_defaults()

    for domain in DOMAIN_FILES:
        merged = deep_merge(merged, _load_yaml(domain))

    merged = deep_merge(merged, _load_yaml(name))

    env_data = _load_environment(env if env is not None else os.environ)
    merged = deep_merge(merged, env_data)

    if overrides:
        merged = deep_merge(merged, _flatten_overrides(overrides))

    validate_settings(merged)
    return Settings(**merged)


def _load_yaml(name: str) -> dict[str, Any]:
    path = DEFAULT_CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        if name in ("development", "production"):
            raise ConfigurationError(
                f"Required config file not found: {path}"
            )
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ConfigurationError(
            f"Config file {path} must contain a top-level mapping, got "
            f"{type(data).__name__}"
        )
    return data


def _load_environment(env: Mapping[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, raw in env.items():
        if not key.startswith(_ENV_PREFIX):
            continue
        stripped = key[len(_ENV_PREFIX):]
        if not stripped:
            continue
        result = _set_path(result, stripped.lower(), _coerce(raw))
    return result


def _coerce(raw: str) -> Any:
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "none", "None"):
        return None
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def _set_path(base: dict[str, Any], dotted: str, value: Any) -> dict[str, Any]:
    node = base
    parts = dotted.split("__")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            node = {}
            base[part] = node
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


def get_config(
    name: str = "development",
    *,
    reload: bool = False,
    overrides: Mapping[str, Any] | None = None,
    env: Mapping[str, str] | None = None,
) -> Settings:
    """Return the cached :class:`Settings`, loading it if necessary.

    Pass ``reload=True`` to force a fresh load (useful in tests when the
    environment has changed).
    """
    global _cached
    if _cached is None or reload or overrides is not None or env is not None:
        _cached = load_config(name, overrides=overrides, env=env)
    return _cached


def reset_config() -> None:
    """Drop the cached settings (primarily for testing)."""
    global _cached
    _cached = None
