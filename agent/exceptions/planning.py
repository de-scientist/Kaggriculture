from agent.exceptions.base import KaggricultureError


class PlanningError(KaggricultureError):
    """Raised when task scheduling, priority management, or planning fails."""
