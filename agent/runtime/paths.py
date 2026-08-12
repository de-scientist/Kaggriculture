"""Grid pathfinding over the farm board.

Every in-bounds tile is walkable (the engine even allows walking onto LOCKED
tiles).  We still prefer paths through owned land when both options are equal,
so units do not loiter on locked tiles.
"""

from __future__ import annotations

from collections import deque

from .game import Position


def _neighbors(
    pos: Position, board_size: int, prefer_unlocked: set[Position] | None = None
) -> list[Position]:
    x, y = pos
    out = []
    for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < board_size and 0 <= ny < board_size:
            out.append((nx, ny))
    if prefer_unlocked:
        out.sort(key=lambda p: 0 if p in prefer_unlocked else 1)
    return out


def bfs_path(
    src: Position, dst: Position, board_size: int, prefer_unlocked: set[Position] | None = None
) -> list[Position]:
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


_dist_cache: dict[int, list[int]] = {}


def _dist_matrix(board_size: int) -> list[int]:
    cached = _dist_cache.get(board_size)
    if cached is not None:
        return cached
    n = board_size * board_size
    matrix = [0] * (n * n)
    for y in range(board_size):
        for x in range(board_size):
            src = (x, y)
            src_idx = y * board_size + x
            queue: deque[Position] = deque([src])
            seen: dict[Position, int] = {src: 0}
            while queue:
                cur = queue.popleft()
                cur_idx = cur[1] * board_size + cur[0]
                matrix[src_idx * n + cur_idx] = seen[cur]
                for nb in _neighbors(cur, board_size):
                    if nb not in seen:
                        seen[nb] = seen[cur] + 1
                        queue.append(nb)
    _dist_cache[board_size] = matrix
    return matrix


def distance(src: Position, dst: Position, board_size: int) -> int:
    if src == dst:
        return 0
    matrix = _dist_matrix(board_size)
    n = board_size * board_size
    return matrix[(src[1] * board_size + src[0]) * n + dst[1] * board_size + dst[0]]


def next_step(
    src: Position, dst: Position, board_size: int, prefer_unlocked: set[Position] | None = None
) -> Position | None:
    if src == dst:
        return None
    matrix = _dist_matrix(board_size)
    n = board_size * board_size
    d_src = matrix[(src[1] * board_size + src[0]) * n + dst[1] * board_size + dst[0]]
    best: Position | None = None
    best_d = d_src
    for nb in _neighbors(src, board_size, prefer_unlocked):
        d = matrix[(nb[1] * board_size + nb[0]) * n + dst[1] * board_size + dst[0]]
        if d < best_d:
            best_d = d
            best = nb
    return best


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
