from typing import Dict, Any, List
from ..domain.entities import GameState, Plan
from ..interfaces.action_serializer import IActionSerializer
from ..exceptions import IllegalActionError


class ActionSerializer(IActionSerializer):
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def serialize(self, plan: Plan) -> Dict[str, Any]:
        farmer_action = self._serialize_farmer(plan.farmer_action)
        hand_actions = [self._serialize_hand(a) for a in plan.hand_actions]
        market_orders = [self._serialize_market(o) for o in plan.market_orders]
        return {
            "farmer": farmer_action,
            "hands": hand_actions,
            "market": market_orders,
        }

    def _serialize_farmer(self, action) -> List:
        if action is None:
            return ["PASS"]
        return [action.operation] + action.parameters

    def _serialize_hand(self, action) -> List:
        return [action.operation] + action.parameters

    def _serialize_market(self, order) -> List:
        return [order.operation] + order.parameters