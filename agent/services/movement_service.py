from agent.domain.position import Position


DIRECTIONS = {
    "NORTH": Position(0, -1),
    "SOUTH": Position(0, 1),
    "EAST": Position(1, 0),
    "WEST": Position(-1, 0),
}


def move(position: Position, direction: str) -> Position:
    delta = DIRECTIONS.get(direction)
    if delta is None:
        return position
    return Position(position.x + delta.x, position.y + delta.y)


def distance(pos1: Position, pos2: Position) -> int:
    return pos1.distance_to(pos2)


def neighbors(position: Position) -> list[Position]:
    return position.neighbors()