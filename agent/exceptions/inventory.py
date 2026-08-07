from agent.exceptions.base import KaggricultureError


class InventoryError(KaggricultureError):
    """Raised when an inventory or shed operation is invalid."""

    CAPACITY_EXCEEDED = "capacity_exceeded"
    INSUFFICIENT_ITEMS = "insufficient_items"
    RESERVATION_CONFLICT = "reservation_conflict"
