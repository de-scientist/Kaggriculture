from abc import ABC, abstractmethod
from typing import List, Any
from ..domain.entities import GameState, Intent


class BasePlanner(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def generate(self, state: GameState) -> List[Intent]:
        ...