from typing import Any


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def safe_get(d: dict[str, Any], key: str, default: Any = None) -> Any:
    return d.get(key, default)


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    result.update(override)
    return result
