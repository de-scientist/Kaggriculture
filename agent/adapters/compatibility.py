from __future__ import annotations

OBSERVATION_VERSION = 1


def get_observation_version(obs: dict) -> int:
    return obs.get("_version", OBSERVATION_VERSION)


def normalize_observation(obs: dict) -> dict:
    version = get_observation_version(obs)
    if version > OBSERVATION_VERSION:
        raise CompatibilityError(
            f"Observation version {version} is newer than supported {OBSERVATION_VERSION}"
        )
    return obs


def normalize_action(action: dict) -> dict:
    return action


def get_compatible_field(obs: dict, field: str, default=None):
    return obs.get(field, default)


class CompatibilityError(Exception):
    pass
