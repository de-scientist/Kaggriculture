from __future__ import annotations


class StrategyMetrics:
    __slots__ = (
        "_buy_count",
        "_decision_count",
        "_harvest_count",
        "_idle_count",
        "_sell_count",
        "_total_score",
    )

    def __init__(self) -> None:
        self._decision_count = 0
        self._harvest_count = 0
        self._sell_count = 0
        self._buy_count = 0
        self._idle_count = 0
        self._total_score = 0.0

    @property
    def decision_count(self) -> int:
        return self._decision_count

    @property
    def harvest_count(self) -> int:
        return self._harvest_count

    @property
    def sell_count(self) -> int:
        return self._sell_count

    @property
    def buy_count(self) -> int:
        return self._buy_count

    @property
    def idle_count(self) -> int:
        return self._idle_count

    @property
    def total_score(self) -> float:
        return self._total_score

    def record_decision(self, action_type: str, score: float) -> None:
        self._decision_count += 1
        self._total_score += score
        if action_type == "harvest":
            self._harvest_count += 1
        elif action_type == "sell":
            self._sell_count += 1
        elif action_type in ("buy_seed", "buy_product", "buy_animal"):
            self._buy_count += 1
        elif action_type == "pass":
            self._idle_count += 1

    def average_score(self) -> float:
        if self._decision_count == 0:
            return 0.0
        return self._total_score / self._decision_count

    def harvest_efficiency(self) -> float:
        if self._decision_count == 0:
            return 0.0
        return self._harvest_count / self._decision_count

    def idle_rate(self) -> float:
        if self._decision_count == 0:
            return 0.0
        return self._idle_count / self._decision_count

    def reset(self) -> None:
        self._decision_count = 0
        self._harvest_count = 0
        self._sell_count = 0
        self._buy_count = 0
        self._idle_count = 0
        self._total_score = 0.0
