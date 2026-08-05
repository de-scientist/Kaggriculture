from typing import Protocol, Dict, Any, List
from ..domain.entities import Plan


class IActionSerializer(Protocol):
    def serialize(self, plan: Plan) -> Dict[str, Any]:
        ...