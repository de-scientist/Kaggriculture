from typing import List, Any
from .base_strategy import BaseStrategy
from ..domain.entities import GameState, ScoredIntent, Intent


class DeterministicStrategy(BaseStrategy):
    def score(self, state: GameState, intents: List[Any]) -> List[ScoredIntent]:
        scored = []
        for intent in intents:
            score = self._calculate_score(state, intent)
            scored.append(ScoredIntent(
                intent=intent,
                score=score,
                strategy=self.__class__.__name__,
                confidence=1.0,
            ))
        return scored

    def _calculate_score(self, state: GameState, intent: Intent) -> float:
        op = intent.operation
        if op == "HARVEST":
            return 2.0
        elif op == "SELL":
            return 1.5
        elif op == "PLANT":
            return 1.0
        elif op == "WATER":
            return 0.8
        elif op == "FERTILIZE":
            return 1.2
        elif op == "FEED":
            return 0.9
        elif op == "CARE":
            return 0.7
        elif op == "BUY_SEED":
            return -0.3
        elif op == "BUY_PRODUCT":
            return -0.2
        elif op == "HIRE":
            return -0.5
        elif op == "BUY_LAND":
            return -0.8
        elif op in ("NORTH", "SOUTH", "EAST", "WEST"):
            return 0.1
        elif op == "PASS":
            return 0.0
        else:
            return 0.0