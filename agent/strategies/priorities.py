from __future__ import annotations


PRIORITY_HARVEST = 1
PRIORITY_COLLECT = 2
PRIORITY_FEED = 3
PRIORITY_WATER = 4
PRIORITY_FERTILIZE = 5
PRIORITY_PLANT = 6
PRIORITY_SELL = 7
PRIORITY_BUY = 8
PRIORITY_HIRE = 9
PRIORITY_EXPAND = 10
PRIORITY_IDLE = 11


PRIORITY_MAP = {
    "harvest": PRIORITY_HARVEST,
    "collect": PRIORITY_COLLECT,
    "feed": PRIORITY_FEED,
    "water": PRIORITY_WATER,
    "fertilize": PRIORITY_FERTILIZE,
    "plant": PRIORITY_PLANT,
    "sell": PRIORITY_SELL,
    "buy": PRIORITY_BUY,
    "hire": PRIORITY_HIRE,
    "expand": PRIORITY_EXPAND,
    "pass": PRIORITY_IDLE,
}


def get_priority(action_type: str) -> int:
    return PRIORITY_MAP.get(action_type.lower(), PRIORITY_IDLE)