from __future__ import annotations

import time

from agent.adapters import validators
from agent.utilities.logging import get_logger

logger = get_logger("agent.adapters.action")


class ActionAdapter:
    def convert(self, domain_action: dict) -> dict:
        start = time.perf_counter()
        logger.info("Converting domain action: %s", domain_action)

        validators.validate_action_dict(domain_action)

        kaggle_action = {
            "farmer": self._convert_farmer_op(domain_action.get("farmer", ["PASS"])),
            "hands": [self._convert_hand_op(h) for h in domain_action.get("hands", [])],
            "market": [self._convert_market_op(m) for m in domain_action.get("market", [])],
        }

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("Action converted in %.2f ms", elapsed_ms)
        return kaggle_action

    def _convert_farmer_op(self, op: list) -> list:
        if not isinstance(op, list) or len(op) == 0:
            return ["PASS"]
        valid_actions = {
            "NORTH",
            "SOUTH",
            "EAST",
            "WEST",
            "PASS",
            "PLANT",
            "WATER",
            "HARVEST",
            "FERTILIZE",
            "DIG",
            "BUILD_COOP",
            "BUILD_PASTURE",
            "FEED",
            "COLLECT_FERTILIZER",
            "CARE",
            "PICKUP",
            "PLACE",
            "DROP",
        }
        action = op[0]
        if action not in valid_actions:
            logger.warning("Unknown farmer action: %s, defaulting to PASS", action)
            return ["PASS"]
        return op

    def _convert_hand_op(self, op: list) -> list:
        if not isinstance(op, list) or len(op) == 0:
            return ["PASS"]
        return op

    def _convert_market_op(self, op: list) -> list:
        if not isinstance(op, list) or len(op) == 0:
            return []
        valid_actions = {
            "BUY_SEED",
            "BUY_PRODUCT",
            "BUY_ANIMAL",
            "SELL",
            "HIRE",
            "BUY_LAND",
        }
        action = op[0]
        if action not in valid_actions:
            logger.warning("Unknown market action: %s, skipping", action)
            return []
        return op
