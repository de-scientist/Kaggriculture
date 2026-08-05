from dataclasses import dataclass, field
from typing import List


@dataclass
class TownState:
    unlocked_shops: List[str] = field(default_factory=list)