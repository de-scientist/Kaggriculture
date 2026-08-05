from typing import List, Any
from .base_planner import BasePlanner
from ...domain.entities import GameState, Intent, IntentType


class WorkerScheduler(BasePlanner):
    def generate(self, state: GameState) -> List[Intent]:
        intents = []
        if self._should_hire(state):
            intents.append(Intent(
                operation="HIRE",
                parameters=[],
                unit_type="market",
                intent_type=IntentType.HIRE,
            ))
        return intents

    def _should_hire(self, state: GameState) -> bool:
        return True