import json

from agent.domain import game_state


def serialize_game_state(state: game_state.GameState) -> dict:
    return {
        "player": state.player,
        "day": state.day,
        "hour": state.hour,
        "step": state.step,
        "farms": state.farms,
        "private": state.private,
        "market": state.market,
        "town": state.town,
    }


def deserialize_game_state(data: dict) -> game_state.GameState:
    return game_state.GameState(
        player=data["player"],
        day=data["day"],
        hour=data["hour"],
        step=data["step"],
        farms=data["farms"],
        private=data["private"],
        market=data["market"],
        town=data["town"],
    )


def serialize_action(action: dict) -> str:
    return json.dumps(action)


def deserialize_action(data: str) -> dict:
    return json.loads(data)
