from __future__ import annotations

from agent.domain.position import Position

DIRECTIONS = {
    "NORTH": Position(0, -1),
    "SOUTH": Position(0, 1),
    "EAST": Position(1, 0),
    "WEST": Position(-1, 0),
}


def distance(pos1: Position, pos2: Position) -> int:
    return pos1.distance_to(pos2)


def reachable(pos: Position, max_distance: int) -> list[Position]:
    result = []
    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):
            if abs(dx) + abs(dy) <= max_distance:
                result.append(Position(pos.x + dx, pos.y + dy))
    return result


def move_cost(from_pos: Position, to_pos: Position) -> int:
    return distance(from_pos, to_pos)


def path(from_pos: Position, to_pos: Position) -> list[Position]:
    if from_pos == to_pos:
        return [from_pos]
    result = [from_pos]
    current = from_pos
    while current != to_pos:
        dx = to_pos.x - current.x
        dy = to_pos.y - current.y
        if abs(dx) >= abs(dy):
            step = Position(current.x + (1 if dx > 0 else -1), current.y)
        else:
            step = Position(current.x, current.y + (1 if dy > 0 else -1))
        result.append(step)
        current = step
    return result


def adjacent(pos: Position) -> list[Position]:
    return pos.neighbors()
