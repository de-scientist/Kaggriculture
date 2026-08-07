from agent.exceptions.base import KaggricultureError


class MovementError(KaggricultureError):
    """Raised when a worker movement or pathfinding operation fails."""
