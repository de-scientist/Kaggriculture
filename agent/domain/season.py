from dataclasses import dataclass


@dataclass
class Season:
    total_days: int = 30
    turns_per_day: int = 24
    total_turns: int = 720
