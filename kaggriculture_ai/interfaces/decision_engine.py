from typing import Protocol, List, Any, Dict
from ..domain.entities import GameState, Plan


class IDecisionEngine(Protocol):
    def generate_candidates(self, state: GameState) -> List[Any]:
        ...

    def validate_actions(self, state: GameState, candidates: List[Any]) -> List[Any]:
        ...

    def score_intents(self, state: GameState, intents: List[Any]) -> List[Any]:
        ...

    def choose_actions(self, state: GameState, scored_intents: List[Any]) -> Plan:
        ...