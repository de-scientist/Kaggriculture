from typing import Any


def create_worker(position: list[int]) -> dict[str, Any]:
    return {"position": position, "inventory": {}, "busy": False}


def count_hires(hires_today: int) -> int:
    return hires_today
