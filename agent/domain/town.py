from dataclasses import dataclass, field


@dataclass
class TownState:
    unlocked_shops: list[str] = field(default_factory=list)
