def validate_position(position: list, board_size: int) -> bool:
    x, y = position
    return 0 <= x < board_size and 0 <= y < board_size


def validate_tile(tile: dict) -> bool:
    if tile is None:
        return True
    if isinstance(tile, dict):
        return True
    return False


def validate_market_order(order: list) -> bool:
    if not isinstance(order, list):
        return False
    if len(order) < 1:
        return False
    return True
