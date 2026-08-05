from typing import List, Any
from .base_planner import BasePlanner
from ...domain.entities import GameState, Intent, IntentType


class MarketPlanner(BasePlanner):
    def generate(self, state: GameState) -> List[Intent]:
        intents = []
        shed = state.raw.get("private", {}).get("shed", {})
        for product, quantity in shed.items():
            if quantity > 0 and product != "FERTILIZER":
                intents.append(Intent(
                    operation="SELL",
                    parameters=[product, str(quantity)],
                    unit_type="market",
                    intent_type=IntentType.SELL,
                ))
        return intents