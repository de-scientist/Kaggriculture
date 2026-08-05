from typing import List, Any, Optional, Tuple
from .base_planner import BasePlanner
from ...domain.entities import GameState, Intent, IntentType


class CropPlanner(BasePlanner):
    def generate(self, state: GameState) -> List[Intent]:
        intents = []
        for crop_type in self.config.get("crops", ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]):
            crop_intents = self._generate_crop_intents(state, crop_type)
            intents.extend(crop_intents)
        return intents

    def _generate_crop_intents(self, state: GameState, crop_type: str) -> List[Intent]:
        intents = []
        seeds = state.raw.get("private", {}).get("seeds", {}).get(crop_type, 0)
        if seeds > 0:
            empty_tile = self._find_empty_tile(state)
            if empty_tile:
                intents.append(Intent(
                    operation="PLANT",
                    parameters=[crop_type],
                    x=empty_tile[0],
                    y=empty_tile[1],
                    unit_type="farmer",
                    intent_type=IntentType.PLANT,
                ))
        return intents

    def _find_empty_tile(self, state: GameState) -> Optional[Tuple[int, int]]:
        tiles = state.raw.get("farms", [{}])[0].get("tiles", [])
        for y, row in enumerate(tiles):
            for x, cell in enumerate(row):
                if cell is None:
                    return (x, y)
        return None