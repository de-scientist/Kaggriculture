from __future__ import annotations

import json


def serialize_game_state(state: object) -> str:
    data = {
        "player": getattr(state, "player", 0),
        "day": getattr(state, "current_day", lambda: 0)(),
        "turn": getattr(state, "current_turn", lambda: 0)(),
        "money": getattr(state, "available_money", lambda: 0.0)(),
    }
    return json.dumps(data)


def deserialize_game_state(data: str) -> dict:
    return json.loads(data)


def serialize_action(action: dict) -> str:
    return json.dumps(action)


def deserialize_action(data: str) -> dict:
    return json.loads(data)


def serialize_market_order(order: list) -> str:
    return json.dumps(order)


def deserialize_market_order(data: str) -> list:
    return json.loads(data)
