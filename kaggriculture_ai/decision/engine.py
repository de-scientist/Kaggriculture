from typing import List, Any, Dict
from .strategies.base_strategy import BaseStrategy
from .planners.base_planner import BasePlanner
from ..domain.entities import GameState, Plan, Intent
from ..exceptions import BudgetExceededError


class DecisionEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.planners: List[BasePlanner] = []
        self.strategy: BaseStrategy = None

    def register_planner(self, planner: BasePlanner) -> None:
        self.planners.append(planner)

    def register_strategy(self, strategy: BaseStrategy) -> None:
        self.strategy = strategy

    def generate_candidates(self, state: GameState) -> List[Intent]:
        all_candidates = []
        for planner in self.planners:
            candidates = planner.generate(state)
            all_candidates.extend(candidates)
        return all_candidates

    def validate_actions(self, state: GameState, candidates: List[Intent]) -> List[Intent]:
        valid_intents = []
        for candidate in candidates:
            if self._validate_intent(state, candidate):
                valid_intents.append(candidate)
        return valid_intents

    def _validate_intent(self, state: GameState, intent: Intent) -> bool:
        if intent.operation == "PLANT":
            return self._validate_plant(state, intent)
        elif intent.operation == "WATER":
            return self._validate_water(state, intent)
        elif intent.operation == "HARVEST":
            return self._validate_harvest(state, intent)
        elif intent.operation == "SELL":
            return self._validate_sell(state, intent)
        elif intent.operation == "BUY_SEED":
            return self._validate_buy_seed(state, intent)
        elif intent.operation == "BUY_PRODUCT":
            return self._validate_buy_product(state, intent)
        elif intent.operation == "BUY_ANIMAL":
            return self._validate_buy_animal(state, intent)
        elif intent.operation == "HIRE":
            return self._validate_hire(state, intent)
        elif intent.operation == "BUY_LAND":
            return self._validate_buy_land(state, intent)
        elif intent.operation in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"):
            return True
        elif intent.operation in ("BUILD_COOP", "BUILD_PASTURE"):
            return self._validate_build(state, intent)
        elif intent.operation == "DIG":
            return self._validate_dig(state, intent)
        elif intent.operation == "FEED":
            return self._validate_feed(state, intent)
        elif intent.operation == "CARE":
            return self._validate_care(state, intent)
        elif intent.operation == "COLLECT_FERTILIZER":
            return self._validate_collect_fertilizer(state, intent)
        elif intent.operation == "FERTILIZE":
            return self._validate_fertilize(state, intent)
        elif intent.operation == "PLACE":
            return self._validate_place(state, intent)
        elif intent.operation == "PICKUP":
            return self._validate_pickup(state, intent)
        elif intent.operation == "DROP":
            return self._validate_drop(state, intent)
        return True

    def _validate_plant(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_water(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_harvest(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_sell(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_buy_seed(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_buy_product(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_buy_animal(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_hire(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_buy_land(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_build(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_dig(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_feed(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_care(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_collect_fertilizer(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_fertilize(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_place(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_pickup(self, state: GameState, intent: Intent) -> bool:
        return True

    def _validate_drop(self, state: GameState, intent: Intent) -> bool:
        return True

    def score_intents(self, state: GameState, intents: List[Intent]) -> List[Any]:
        if not self.strategy:
            raise RuntimeError("No strategy registered")
        return self.strategy.score(state, intents)

    def choose_actions(self, state: GameState, scored_intents: List[Any]) -> Plan:
        farmer_intents = [i for i in scored_intents if i.unit_type == "farmer"]
        hand_intents = [i for i in scored_intents if i.unit_type == "hand"]
        market_orders = [i for i in scored_intents if i.unit_type == "market"]

        farmer_action = self._select_best(farmer_intents)
        hand_actions = self._select_hand_actions(state, hand_intents)
        market_orders = self._build_market_orders(market_orders)

        return Plan(
            farmer_action=farmer_action,
            hand_actions=hand_actions,
            market_orders=market_orders,
        )

    def _select_best(self, intents: List[Any]) -> Any:
        if not intents:
            return None
        sorted_intents = sorted(intents, key=lambda x: x.score, reverse=True)
        return sorted_intents[0]

    def _select_hand_actions(self, state: GameState, intents: List[Any]) -> List[Any]:
        sorted_intents = sorted(intents, key=lambda x: x.score, reverse=True)
        selected = []
        used_tiles = set()
        for intent in sorted_intents:
            if self._is_action_valid(state, intent, used_tiles):
                selected.append(intent)
                used_tiles.add((intent.x, intent.y))
        return selected

    def _is_action_valid(self, state: GameState, intent: Any, used_tiles: set) -> bool:
        return True

    def _build_market_orders(self, market_intents: List[Any]) -> List[Any]:
        return market_intents[:10]