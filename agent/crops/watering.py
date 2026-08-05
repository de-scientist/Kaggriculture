def bonus_window_start(max_yield_day: int) -> int:
    import math
    return math.ceil(max_yield_day / 2)


def is_in_bonus_window(age: int, max_yield_day: int) -> bool:
    start = bonus_window_start(max_yield_day)
    return start <= age <= max_yield_day


def watering_bonus(watered: bool, fertilized: bool, age: int, max_yield_day: int) -> int:
    if not watered:
        return 0
    if is_in_bonus_window(age, max_yield_day):
        bonus = 1
        if fertilized:
            bonus += 1
        return bonus
    return 0