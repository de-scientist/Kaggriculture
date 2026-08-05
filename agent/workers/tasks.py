def create_task(action: str, target: dict | None = None) -> dict:
    return {"action": action, "target": target}
