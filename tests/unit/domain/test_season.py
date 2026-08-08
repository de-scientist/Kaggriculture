"""Unit tests for the Season domain model (chapter 9)."""
from __future__ import annotations

from agent.domain.season import Season


class TestSeasonConstruction:
    def test_defaults(self) -> None:
        s = Season()
        assert s.day == 0
        assert s.turn == 0
        assert s.turns_per_day == 24
        assert s.total_days == 30
        assert s.total_turns == 720

    def test_custom_values(self) -> None:
        s = Season(day=5, turn=10, turns_per_day=12, total_days=20, total_turns=240)
        assert s.day == 5
        assert s.turn == 10
        assert s.turns_per_day == 12
        assert s.total_days == 20
        assert s.total_turns == 240


class TestSeasonRemaining:
    def test_remaining_turns_at_start(self) -> None:
        s = Season()
        assert s.remaining_turns == 720

    def test_remaining_turns_mid_game(self) -> None:
        s = Season(day=5, turn=0)
        assert s.remaining_turns == 600

    def test_remaining_turns_at_end(self) -> None:
        s = Season(day=29, turn=23)
        assert s.remaining_turns == 1

    def test_remaining_days_at_start(self) -> None:
        s = Season()
        assert s.remaining_days == 30

    def test_remaining_days_mid_game(self) -> None:
        s = Season(day=10)
        assert s.remaining_days == 20

    def test_remaining_days_clamped_at_end(self) -> None:
        s = Season(day=35)
        assert s.remaining_days == 0


class TestSeasonAdvancement:
    def test_advance_turn_within_day(self) -> None:
        s = Season(day=0, turn=5)
        advanced = s.advance_turn()
        assert advanced.day == 0
        assert advanced.turn == 6

    def test_advance_turn_at_day_end(self) -> None:
        s = Season(day=0, turn=23, turns_per_day=24)
        advanced = s.advance_turn()
        assert advanced.day == 1
        assert advanced.turn == 0

    def test_advance_day(self) -> None:
        s = Season(day=5, turn=12)
        advanced = s.advance_day()
        assert advanced.day == 6
        assert advanced.turn == 0

    def test_is_day_complete(self) -> None:
        s = Season(day=0, turn=23, turns_per_day=24)
        assert s.is_day_complete is True

    def test_is_day_not_complete(self) -> None:
        s = Season(day=0, turn=5, turns_per_day=24)
        assert s.is_day_complete is False

    def test_repr(self) -> None:
        s = Season(day=3, turn=10)
        assert "day=3" in repr(s)


class TestSeasonImmutability:
    def test_advance_returns_new_instance(self) -> None:
        s = Season(day=0, turn=5)
        advanced = s.advance_turn()
        assert s is not advanced
        assert s.turn == 5
        assert advanced.turn == 6
