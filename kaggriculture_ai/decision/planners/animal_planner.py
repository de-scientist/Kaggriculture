from typing import List, Any
from .base_planner import BasePlanner
from ...domain.entities import GameState, Intent, IntentType


class AnimalPlanner(BasePlanner):
    def generate(self, state: GameState) -> List[Intent]:
        intents = []
        for animal_type in self.config.get("animals", ["GOOSE", "COW", "SHEEP"]):
            if self._should_buy_animal(state, animal_type):
                intents.append(Intent(
                    operation="BUY_ANIMAL",
                    parameters=[animal_type, "1"],
                    unit_type="market",
                    intent_type=IntentType.BUY_ANIMAL,
                ))
        return intents

    def _should_buy_animal(self, state: GameState, animal_type: str) -> bool:
        return True