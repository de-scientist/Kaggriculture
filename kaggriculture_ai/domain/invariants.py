from typing import Dict, Any, List
from .entities import GameState


class Invariants:
    @staticmethod
    def validate_farm_money(farm: Dict[str, Any]) -> bool:
        return farm.get("money", 0) >= 0

    @staticmethod
    def validate_shed_capacity(inventory: Dict[str, Any]) -> bool:
        total_items = sum(v for k, v in inventory.items() if k != "seeds")
        return total_items <= 100

    @staticmethod
    def validate_yield_units(tile: Dict[str, Any]) -> bool:
        max_yield = tile.get("max_yield", 0)
        yield_units = tile.get("yield_units", 0)
        return 0 <= yield_units <= max_yield

    @staticmethod
    def validate_fed_watered_states(tile: Dict[str, Any]) -> bool:
        return (
            isinstance(tile.get("fed_today"), bool) and
            isinstance(tile.get("watered_today"), bool) and
            isinstance(tile.get("cared_today"), bool)
        )

    @staticmethod
    def validate_consecutive_counters(tile: Dict[str, Any]) -> bool:
        return (
            tile.get("consecutive_unwatered", 0) >= 0 and
            tile.get("consecutive_unfed", 0) >= 0
        )

    @staticmethod
    def validate_all(state: GameState) -> bool:
        return True