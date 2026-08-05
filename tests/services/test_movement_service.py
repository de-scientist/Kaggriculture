from agent.domain.position import Position
from agent.services import movement_service


def test_distance():
    p1 = Position(0, 0)
    p2 = Position(3, 4)
    assert movement_service.distance(p1, p2) == 7


def test_distance_same_position():
    p = Position(2, 3)
    assert movement_service.distance(p, p) == 0


def test_reachable():
    pos = Position(0, 0)
    result = movement_service.reachable(pos, max_distance=1)
    assert Position(0, 0) in result
    assert Position(1, 0) in result
    assert Position(0, 1) in result
    assert Position(-1, 0) in result
    assert Position(0, -1) in result


def test_move_cost():
    p1 = Position(0, 0)
    p2 = Position(3, 4)
    assert movement_service.move_cost(p1, p2) == 7


def test_path():
    from_pos = Position(0, 0)
    to_pos = Position(2, 0)
    result = movement_service.path(from_pos, to_pos)
    assert len(result) == 3
    assert result[0] == from_pos
    assert result[-1] == to_pos


def test_path_same_position():
    pos = Position(2, 3)
    result = movement_service.path(pos, pos)
    assert result == [pos]


def test_adjacent():
    pos = Position(0, 0)
    result = movement_service.adjacent(pos)
    assert len(result) == 4
    assert Position(0, -1) in result
    assert Position(0, 1) in result
    assert Position(-1, 0) in result
    assert Position(1, 0) in result