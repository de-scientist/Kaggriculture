from agent.exceptions.base import KaggricultureError


class CropError(KaggricultureError):
    """Raised when a crop lifecycle operation is invalid or impossible."""
