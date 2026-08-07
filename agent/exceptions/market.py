from agent.exceptions.base import KaggricultureError


class MarketError(KaggricultureError):
    """Raised when a market operation (buy/sell/order) is invalid."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    ORDER_LIMIT_EXCEEDED = "order_limit_exceeded"
    INVALID_PRODUCT = "invalid_product"
