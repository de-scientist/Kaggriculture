from abc import ABC, abstractmethod
from typing import List, Any
from ..domain.entities import GameState, ScoredIntent


class BaseStrategy(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def score(self, state: GameState, intents: List[Any]) -> List[ScoredIntent]:
        ...