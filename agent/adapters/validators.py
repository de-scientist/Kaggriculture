from __future__ import annotations

REQUIRED_OBSERVATION_FIELDS = [
    "player",
    "step",
    "day",
    "hour",
    "farms",
    "private",
    "market",
    "town",
]


def validate_observation_schema(obs: dict) -> None:
    for field in REQUIRED_OBSERVATION_FIELDS:
        if field not in obs:
            raise KeyError(f"Missing required observation field: {field}")


def validate_observation_not_none(obs: dict) -> None:
    if obs is None:
        raise ValueError("Observation cannot be None")


def validate_player_index(obs: dict) -> None:
    player = obs.get("player")
    if not isinstance(player, int):
        raise TypeError(f"Player index must be int, got {type(player)}")
    if player < 0:
        raise ValueError(f"Player index cannot be negative: {player}")


def validate_tile(tile: object, x: int, y: int) -> None:
    if tile is None:
        return
    if isinstance(tile, dict):
        kind = tile.get("kind")
        if kind not in ("PLANT", "WEED", "COOP", "PASTURE", None):
            raise ValueError(f"Invalid tile kind at ({x}, {y}): {kind}")
        return
    raise TypeError(f"Invalid tile type at ({x}, {y}): {type(tile)}")


def validate_market_order(order: list) -> None:
    if not isinstance(order, list):
        raise TypeError(f"Market order must be a list, got {type(order)}")
    if len(order) < 1:
        raise ValueError("Market order cannot be empty")


def validate_action_dict(action: dict) -> None:
    if not isinstance(action, dict):
        raise TypeError(f"Action must be a dict, got {type(action)}")
    for key in ("hands", "market"):
        if key not in action:
            raise KeyError(f"Action missing required key: {key}")


def validate_position(pos: list, board_size: int = 10) -> None:
    if not isinstance(pos, list) or len(pos) != 2:
        raise ValueError(f"Position must be a list of 2 ints, got {pos}")
    x, y = pos
    if not (0 <= x < board_size and 0 <= y < board_size):
        raise ValueError(f"Position ({x}, {y}) out of bounds for board size {board_size}")
