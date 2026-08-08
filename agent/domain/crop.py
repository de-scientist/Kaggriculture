from __future__ import annotations


class Crop:
    __slots__ = (
        "_consecutive_unwatered",
        "_crop_type",
        "_fertilized_until_day",
        "_harvested",
        "_max_lifespan_step",
        "_planted_day",
        "_watered_today",
        "_yield_units",
    )

    def __init__(
        self,
        crop_type: str,
        planted_day: int = 0,
        max_lifespan_step: int = 10,
    ) -> None:
        self._crop_type = crop_type
        self._planted_day = planted_day
        self._watered_today = False
        self._consecutive_unwatered = 0
        self._yield_units = 0
        self._max_lifespan_step = max_lifespan_step
        self._fertilized_until_day = -1
        self._harvested = False

    @property
    def crop_type(self) -> str:
        return self._crop_type

    @property
    def planted_day(self) -> int:
        return self._planted_day

    @property
    def watered_today(self) -> bool:
        return self._watered_today

    @property
    def consecutive_unwatered(self) -> int:
        return self._consecutive_unwatered

    @property
    def yield_units(self) -> int:
        return self._yield_units

    @property
    def max_lifespan_step(self) -> int:
        return self._max_lifespan_step

    @property
    def fertilized_until_day(self) -> int:
        return self._fertilized_until_day

    @property
    def is_harvested(self) -> bool:
        return self._harvested

    def is_mature(self, current_day: int) -> bool:
        return (current_day - self._planted_day) >= 2

    def is_alive(self, current_day: int) -> bool:
        return (current_day - self._planted_day) <= self._max_lifespan_step + 1

    def is_in_bonus_window(self, current_day: int) -> bool:
        bonus_start = (self._max_lifespan_step + 1) // 2
        return bonus_start <= (current_day - self._planted_day) <= self._max_lifespan_step

    def water(self) -> Crop:
        if self._harvested:
            raise ValueError("Cannot water a harvested crop")
        watered = Crop(
            crop_type=self._crop_type,
            planted_day=self._planted_day,
            max_lifespan_step=self._max_lifespan_step,
        )
        watered._watered_today = True
        watered._consecutive_unwatered = self._consecutive_unwatered
        watered._yield_units = self._yield_units
        watered._fertilized_until_day = self._fertilized_until_day
        return watered

    def skip_water(self) -> Crop:
        if self._harvested:
            raise ValueError("Cannot skip water on a harvested crop")
        skipped = Crop(
            crop_type=self._crop_type,
            planted_day=self._planted_day,
            max_lifespan_step=self._max_lifespan_step,
        )
        skipped._watered_today = False
        skipped._consecutive_unwatered = self._consecutive_unwatered + 1
        skipped._yield_units = self._yield_units
        skipped._fertilized_until_day = self._fertilized_until_day
        return skipped

    def fertilize(self, current_day: int) -> Crop:
        if self._harvested:
            raise ValueError("Cannot fertilize a harvested crop")
        fert = Crop(
            crop_type=self._crop_type,
            planted_day=self._planted_day,
            max_lifespan_step=self._max_lifespan_step,
        )
        fert._watered_today = self._watered_today
        fert._consecutive_unwatered = self._consecutive_unwatered
        fert._yield_units = self._yield_units
        fert._fertilized_until_day = current_day + 3
        return fert

    def grow(self, current_day: int) -> Crop:
        if self._harvested:
            raise ValueError("Cannot grow a harvested crop")
        grown = Crop(
            crop_type=self._crop_type,
            planted_day=self._planted_day,
            max_lifespan_step=self._max_lifespan_step,
        )
        grown._watered_today = self._watered_today
        grown._consecutive_unwatered = self._consecutive_unwatered
        grown._fertilized_until_day = self._fertilized_until_day
        bonus = 0
        if self._watered_today:
            bonus += 1
        if self._fertilized_until_day >= current_day:
            bonus += 1
        grown._yield_units = bonus
        return grown

    def harvest(self) -> Crop:
        if self._harvested:
            raise ValueError("Cannot harvest an already harvested crop")
        harvested = Crop(
            crop_type=self._crop_type,
            planted_day=self._planted_day,
            max_lifespan_step=self._max_lifespan_step,
        )
        harvested._harvested = True
        harvested._yield_units = self._yield_units
        return harvested

    def __repr__(self) -> str:
        return (
            f"Crop(type={self._crop_type!r}, day={self._planted_day}, "
            f"yield={self._yield_units}, harvested={self._harvested})"
        )
