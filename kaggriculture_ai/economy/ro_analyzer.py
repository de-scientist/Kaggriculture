from typing import Dict, Any


class ROIAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def calculate_roi(self, state: Any, intent: Any) -> Dict[str, float]:
        return {
            "immediate_money": 0.0,
            "payoff_delay": 0.0,
            "risk": 0.0,
            "resource_fit": 0.0,
        }