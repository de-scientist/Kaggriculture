def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(value, max_val))


def safe_get(d: dict, key: str, default=None):
    return d.get(key, default)


def merge_dicts(base: dict, override: dict) -> dict:
    result = base.copy()
    result.update(override)
    return result