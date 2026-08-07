"""Application configuration service.

Public entry points:
    - :func:`get_config` / :func:`load_config` -> immutable :class:`Settings`
    - :func:`reset_config` (test helper)
    - :class:`Settings`, :func:`validate_settings`
    - :data:`DEFAULTS`, :func:`schema_defaults`, :func:`deep_merge`
"""

from agent.config.loader import get_config, load_config, reset_config
from agent.config.schema import DEFAULTS, deep_merge, schema_defaults
from agent.config.settings import Settings
from agent.config.validators import validate_settings


def is_feature_enabled(flag: str) -> bool:
    """Return whether a feature flag is enabled in the loaded configuration."""
    try:
        return get_config().is_feature_enabled(flag)
    except Exception:
        return bool(__import__("os").environ.get(flag, "").lower() in ("1", "true", "yes"))


__all__ = [
    "DEFAULTS",
    "Settings",
    "deep_merge",
    "get_config",
    "is_feature_enabled",
    "load_config",
    "reset_config",
    "schema_defaults",
    "validate_settings",
]
