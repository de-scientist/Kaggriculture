from agent.exceptions.base import KaggricultureError


class StrategyError(KaggricultureError):
    """Raised when strategy selection, evaluation, or execution fails."""
