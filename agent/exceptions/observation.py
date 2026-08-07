from agent.exceptions.base import KaggricultureError


class ObservationError(KaggricultureError):
    """Raised when an observation cannot be parsed or is malformed."""
