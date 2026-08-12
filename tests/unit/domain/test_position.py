"""Unit tests for the Position domain model (chapter 9)."""

from __future__ import annotations

from agent.domain.position import Position


class TestPositionConstruction:
    def test_values(self) -> None:
        pos = Position(3, 5)
        assert pos.x == 3
        assert pos.y == 5

    def test_zero_position(self) -> None:
        pos = Position(0, 0)
        assert pos.x == 0
        assert pos.y == 0


class TestPositionDistance:
    def test_same_position(self) -> None:
        pos = Position(0, 0)
        assert pos.distance_to(Position(0, 0)) == 0

    def test_horizontal_distance(self) -> None:
        assert Position(0, 0).distance_to(Position(5, 0)) == 5

    def test_vertical_distance(self) -> None:
        assert Position(0, 0).distance_to(Position(0, 5)) == 5

    def test_diagonal_distance(self) -> None:
        assert Position(0, 0).distance_to(Position(3, 4)) == 7

    def test_negative_coordinates(self) -> None:
        assert Position(-3, -4).distance_to(Position(0, 0)) == 7


class TestPositionNeighbors:
    def test_has_four_neighbors(self) -> None:
        pos = Position(5, 5)
        neighbors = pos.neighbors()
        assert len(neighbors) == 4

    def test_neighbors_include_all_directions(self) -> None:
        pos = Position(5, 5)
        neighbors = pos.neighbors()
        pos_set = {(p.x, p.y) for p in neighbors}
        assert (5, 4) in pos_set  # north
        assert (5, 6) in pos_set  # south
        assert (4, 5) in pos_set  # west
        assert (6, 5) in pos_set  # east


class TestPositionEquality:
    def test_equal_positions(self) -> None:
        assert Position(1, 2) == Position(1, 2)

    def test_different_positions_not_equal(self) -> None:
        assert Position(1, 2) != Position(3, 4)

    def test_equal_to_non_position(self) -> None:
        assert (Position(1, 2) == "string") is False

    def test_hashable(self) -> None:
        pos = Position(1, 2)
        assert hash(pos) == hash(Position(1, 2))
        assert pos in {Position(1, 2), Position(3, 4)}

    def test_repr(self) -> None:
        pos = Position(7, 3)
        assert "7" in repr(pos)
        assert "3" in repr(pos)
