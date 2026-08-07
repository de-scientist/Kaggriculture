from agent.exceptions.base import KaggricultureError


class WorkerError(KaggricultureError):
    """Raised when farmer or farm-hand scheduling/assignment fails."""
