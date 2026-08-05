from typing import List, Any
from .base_planner import BasePlanner
from ...domain.entities import GameState, Intent, IntentType


class ExpansionPlanner(BasePlanner):
    def generate(self, state: GameState) -> List[Intent]:
        intents = []
        if self._should_expand(state):
            intents.append(Intent(
                operation="BUY_LAND",
                parameters=[],
                unit_type="market",
                intent_type=IntentType.BUY_LAND,
            ))
        return intents

    def _should_expand(self, state: GameState) -> bool:
        return False