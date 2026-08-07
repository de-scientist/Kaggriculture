from agent.exceptions.base import KaggricultureError


class ValidationError(KaggricultureError):
    """Raised when an observation, action, or state fails invariant checks."""
