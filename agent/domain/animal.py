from __future__ import annotations


class Animal:
    __slots__ = (
        "_animal_type",
        "_hunger",
        "_production_timer",
        "_producing",
        "_health",
        "_housing",
        "_fed_today",
        "_consecutive_unfed",
        "_cared_today",
        "_fertilizer_available",
        "_pending_care_bonus",
        "_escaped",
    )

    def __init__(
        self,
        animal_type: str,
        housing: str = "NONE",
    ) -> None:
        self._animal_type = animal_type
        self._hunger = 0
        self._production_timer = 0
        self._producing = False
        self._health = 100
        self._housing = housing
        self._fed_today = False
        self._consecutive_unfed = 0
        self._cared_today = False
        self._fertilizer_available = False
        self._pending_care_bonus = 0
        self._escaped = False

    @property
    def animal_type(self) -> str:
        return self._animal_type

    @property
    def housing(self) -> str:
        return self._housing

    @property
    def hunger(self) -> int:
        return self._hunger

    @property
    def health(self) -> int:
        return self._health

    @property
    def fed_today(self) -> bool:
        return self._fed_today

    @property
    def consecutive_unfed(self) -> int:
        return self._consecutive_unfed

    @property
    def cared_today(self) -> bool:
        return self._cared_today

    @property
    def fertilizer_available(self) -> bool:
        return self._fertilizer_available

    @property
    def pending_care_bonus(self) -> int:
        return self._pending_care_bonus

    @property
    def is_escaped(self) -> bool:
        return self._escaped

    @property
    def is_alive(self) -> bool:
        return not self._escaped and self._health > 0

    def feed(self) -> Animal:
        if self._escaped:
            raise ValueError("Cannot feed an escaped animal")
        fed = Animal(
            animal_type=self._animal_type,
            housing=self._housing,
        )
        fed._hunger = 0
        fed._production_timer = self._production_timer
        fed._producing = self._producing
        fed._health = self._health
        fed._fed_today = True
        fed._consecutive_unfed = 0
        fed._cared_today = self._cared_today
        fed._fertilizer_available = self._fertilizer_available
        fed._pending_care_bonus = self._pending_care_bonus
        fed._escaped = self._escaped
        return fed

    def skip_feed(self) -> Animal:
        if self._escaped:
            raise ValueError("Cannot skip feed on an escaped animal")
        skipped = Animal(
            animal_type=self._animal_type,
            housing=self._housing,
        )
        skipped._hunger = self._hunger + 1
        skipped._production_timer = self._production_timer
        skipped._producing = self._producing
        skipped._health = self._health
        skipped._fed_today = False
        skipped._consecutive_unfed = self._consecutive_unfed + 1
        skipped._cared_today = self._cared_today
        skipped._fertilizer_available = self._fertilizer_available
        skipped._pending_care_bonus = self._pending_care_bonus
        skipped._escaped = self._consecutive_unfed + 1 >= 2
        return skipped

    def care(self) -> Animal:
        if self._escaped:
            raise ValueError("Cannot care for an escaped animal")
        cared = Animal(
            animal_type=self._animal_type,
            housing=self._housing,
        )
        cared._hunger = self._hunger
        cared._production_timer = self._production_timer
        cared._producing = self._producing
        cared._health = self._health
        cared._fed_today = self._fed_today
        cared._consecutive_unfed = self._consecutive_unfed
        cared._cared_today = True
        cared._fertilizer_available = self._fertilizer_available
        cared._pending_care_bonus = self._pending_care_bonus + 1
        cared._escaped = self._escaped
        return cared

    def produce(self) -> tuple[Animal, int]:
        if self._escaped:
            raise ValueError("Escaped animal cannot produce")
        if not self._fed_today:
            raise ValueError("Animal must be fed before producing")
        if self._pending_care_bonus > 0:
            bonus = self._pending_care_bonus
            cared = Animal(
                animal_type=self._animal_type,
                housing=self._housing,
            )
            cared._hunger = self._hunger
            cared._production_timer = self._production_timer
            cared._producing = self._producing
            cared._health = self._health
            cared._fed_today = self._fed_today
            cared._consecutive_unfed = self._consecutive_unfed
            cared._cared_today = False
            cared._fertilizer_available = self._fertilizer_available
            cared._pending_care_bonus = 0
            cared._escaped = self._escaped
            return cared, bonus
        return self, 0

    def collect_fertilizer(self) -> tuple[Animal, int]:
        if self._escaped:
            raise ValueError("Escaped animal cannot produce fertilizer")
        if not self._fertilizer_available:
            raise ValueError("No fertilizer available to collect")
        fert = Animal(
            animal_type=self._animal_type,
            housing=self._housing,
        )
        fert._hunger = self._hunger
        fert._production_timer = self._production_timer
        fert._producing = self._producing
        fert._health = self._health
        fert._fed_today = self._fed_today
        fert._consecutive_unfed = self._consecutive_unfed
        fert._cared_today = self._cared_today
        fert._fertilizer_available = False
        fert._pending_care_bonus = self._pending_care_bonus
        fert._escaped = self._escaped
        return fert, 1

    def __repr__(self) -> str:
        return (
            f"Animal(type={self._animal_type!r}, hunger={self._hunger}, "
            f"health={self._health}, escaped={self._escaped})"
        )