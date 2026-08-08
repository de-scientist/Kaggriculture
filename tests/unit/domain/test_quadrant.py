"""Unit tests for the Farm module (quadrants) (chapter 9)."""
from __future__ import annotations

from agent.domain.quadrant import Quadrant


class TestQuadrant:
    def test_defaults(self) -> None:
        q = Quadrant()
        assert q.name == "NW"
        assert q.unlocked is False
        assert q.cost == 0
        assert q.owner == 0

    def test_custom_values(self) -> None:
        q = Quadrant(name="NE", unlocked=True, cost=1000, owner=0)
        assert q.name == "NE"
        assert q.unlocked is True
        assert q.cost == 1000

    def test_unlock(self) -> None:
        q = Quadrant(name="NE", cost=1000)
        unlocked = q.unlock(owner=0)
        assert unlocked.unlocked is True
        assert unlocked.owner == 0
        assert q.unlocked is False

    def test_repr(self) -> None:
        q = Quadrant(name="NW")
        assert "NW" in repr(q)
