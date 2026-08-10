from __future__ import annotations

import json

from typing import Any


def serialize_game_state(state: object) -> str:
    data: dict[str, Any] = {
        "player": getattr(state, "player", 0),
        "day": getattr(state, "current_day", lambda: 0)(),
        "turn": getattr(state, "current_turn", lambda: 0)(),
        "money": getattr(state, "available_money", lambda: 0.0)(),
    }
    return json.dumps(data)


def deserialize_game_state(data: str) -> dict[str, Any]:
    return dict(json.loads(data))


def serialize_action(action: dict[str, Any]) -> str:
    return json.dumps(action)


def deserialize_action(data: str) -> dict[str, Any]:
    return dict(json.loads(data))


def serialize_market_order(order: list[Any]) -> str:
    return json.dumps(order)


def deserialize_market_order(data: str) -> list[Any]:
    return list(json.loads(data))
