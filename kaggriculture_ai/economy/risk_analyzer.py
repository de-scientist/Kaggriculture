from typing import Dict, Any


class RiskAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def evaluate(self, state: Any, intent: Any) -> float:
        return 0.0