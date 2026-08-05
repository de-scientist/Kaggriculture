from agent.domain import crop as crop_domain


def track(tile: dict) -> dict:
    if tile is None or not isinstance(tile, dict):
        return {}
    return tile