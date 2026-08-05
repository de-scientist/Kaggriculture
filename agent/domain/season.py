from __future__ import annotations


class Season:
    __slots__ = ("_day", "_total_days", "_total_turns", "_turn", "_turns_per_day")

    def __init__(
        self,
        day: int = 0,
        turn: int = 0,
        turns_per_day: int = 24,
        total_days: int = 30,
        total_turns: int = 720,
    ) -> None:
        self._day = day
        self._turn = turn
        self._turns_per_day = turns_per_day
        self._total_days = total_days
        self._total_turns = total_turns

    @property
    def day(self) -> int:
        return self._day

    @property
    def turn(self) -> int:
        return self._turn

    @property
    def turns_per_day(self) -> int:
        return self._turns_per_day

    @property
    def total_days(self) -> int:
        return self._total_days

    @property
    def total_turns(self) -> int:
        return self._total_turns

    @property
    def remaining_turns(self) -> int:
        return max(0, self._total_turns - self._turn)

    @property
    def remaining_days(self) -> int:
        return max(0, self._total_days - self._day)

    @property
    def is_day_complete(self) -> bool:
        return self._turn >= self._turns_per_day - 1

    def advance_turn(self) -> Season:
        new_turn = self._turn + 1
        new_day = self._day
        if new_turn >= self._turns_per_day:
            new_turn = 0
            new_day = self._day + 1
        return Season(
            day=new_day,
            turn=new_turn,
            turns_per_day=self._turns_per_day,
            total_days=self._total_days,
            total_turns=self._total_turns,
        )

    def advance_day(self) -> Season:
        return Season(
            day=self._day + 1,
            turn=0,
            turns_per_day=self._turns_per_day,
            total_days=self._total_days,
            total_turns=self._total_turns,
        )

    def __repr__(self) -> str:
        return (
            f"Season(day={self._day}, turn={self._turn}, "
            f"remaining_turns={self.remaining_turns})"
        )
