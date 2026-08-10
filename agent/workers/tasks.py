from typing import Any


def create_task(action: str, target: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"action": action, "target": target}
