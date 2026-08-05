from typing import Protocol, Dict, Any
from ..domain.entities import GameState


class IObservationAdapter(Protocol):
    def adapt(self, raw_observation: Dict[str, Any]) -> GameState:
        ...

    def last_raw(self) -> Dict[str, Any]:
        ...