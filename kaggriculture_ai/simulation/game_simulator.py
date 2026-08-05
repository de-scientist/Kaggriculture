from typing import Dict, Any
from ..domain.entities import GameState, Plan


class GameSimulator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def step(self, state: GameState, plan: Plan) -> GameState:
        return state

    def clone(self, state: GameState) -> GameState:
        return state