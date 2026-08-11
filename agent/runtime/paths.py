"""Grid pathfinding over the farm board.

Every in-bounds tile is walkable (the engine even allows walking onto LOCKED
tiles).  We still prefer paths through owned land when both options are equal,
so units do not loiter on locked tiles.
"""

from __future__ import annotations

from collections import deque

from .game import Position


def _neighbors(pos: Position, board_size: int, prefer_unlocked: set[Position] | None = None) -> list[Position]:
    x, y = pos
    out = []
    for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < board_size and 0 <= ny < board_size:
            out.append((nx, ny))
    if prefer_unlocked:
        out.sort(key=lambda p: 0 if p in prefer_unlocked else 1)
    return out


def bfs_path(src: Position, dst: Position, board_size: int, prefer_unlocked: set[Position] | None = None) -> list[Position]:
    """Shortest path from src to dst (inclusive). Returns [] if src == dst."""
    if src == dst:
        return []
    queue: deque[Position] = deque([src])
    prev: dict[Position, Position] = {src: src}
    while queue:
        cur = queue.popleft()
        if cur == dst:
            break
        for nb in _neighbors(cur, board_size, prefer_unlocked):
            if nb not in prev:
                prev[nb] = cur
                queue.append(nb)
    if dst not in prev:
        return []
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    path.reverse()
    return path


def next_step(src: Position, dst: Position, board_size: int, prefer_unlocked: set[Position] | None = None) -> Position | None:
    path = bfs_path(src, dst, board_size, prefer_unlocked)
    if len(path) < 2:
        return None
    return path[1]


def distance(src: Position, dst: Position, board_size: int) -> int:
    if src == dst:
        return 0
    path = bfs_path(src, dst, board_size)
    return len(path) - 1


def nearest_shed_tile(pos: Position, board_size: int) -> Position:
    best: Position = (0, 0)
    best_len = 10**9
    for tile in ((4, 4), (5, 4), (4, 5), (5, 5)):
        if tile[0] >= board_size or tile[1] >= board_size:
            continue
        d = distance(pos, tile, board_size)
        if d < best_len:
            best_len = d
            best = tile
    return best


def move_op_for_next_step(current: Position, nxt: Position) -> str | None:
    dx = nxt[0] - current[0]
    dy = nxt[1] - current[1]
    if (dx, dy) == (0, -1):
        return "NORTH"
    if (dx, dy) == (0, 1):
        return "SOUTH"
    if (dx, dy) == (1, 0):
        return "EAST"
    if (dx, dy) == (-1, 0):
        return "WEST"
    return None
