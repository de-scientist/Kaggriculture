from agent.domain.position import Position


def validate_position(position: Position, board_size: int) -> bool:
    return 0 <= position.x < board_size and 0 <= position.y < board_size


def validate_tile(tile: object) -> bool:
    return tile is None or isinstance(tile, object)


def validate_market_order(order: list) -> bool:
    return isinstance(order, list) and len(order) >= 1