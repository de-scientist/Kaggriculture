from __future__ import annotations

from typing import Any

OBSERVATION_VERSION = 1


def get_observation_version(obs: dict[str, Any]) -> int:
    return int(obs.get("_version", OBSERVATION_VERSION))


def normalize_observation(obs: dict[str, Any]) -> dict[str, Any]:
    version = get_observation_version(obs)
    if version > OBSERVATION_VERSION:
        raise CompatibilityError(
            f"Observation version {version} is newer than supported {OBSERVATION_VERSION}"
        )
    return dict(obs)


def normalize_action(action: dict[str, Any]) -> dict[str, Any]:
    return dict(action)


def get_compatible_field(obs: dict[str, Any], field: str, default: Any = None) -> Any:
    return obs.get(field, default)


class CompatibilityError(Exception):
    pass
