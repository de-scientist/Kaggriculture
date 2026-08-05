DIRECTIONS = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST": (1, 0),
    "WEST": (-1, 0),
}


def compute_move(position: list, direction: str) -> list:
    dx, dy = DIRECTIONS.get(direction, (0, 0))
    return [position[0] + dx, position[1] + dy]


def distance(pos1: list, pos2: list) -> int:
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
