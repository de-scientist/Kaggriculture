"""Stage 2 — Price Forecasting.

Simple, conservative price forecasting using moving averages and
exponential smoothing. All forecasts use only historical data available
at or before the current turn (no future leakage).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agent.market.price_tracker import PriceHistory


@dataclass
class PriceForecast:
    """Forecasted price with confidence."""

    product: str
    expected_price: float
    confidence: float
    lower_bound: float
    upper_bound: float
    trend: str  # "rising", "falling", "stable"
    method: str


class PriceForecaster:
    """Forecasts future prices using simple, conservative methods.

    Supports:
    - Simple moving average (default)
    - Exponential smoothing
    - Linear trend estimation
    """

    def __init__(self, lookback: int = 10, smoothing_alpha: float = 0.3) -> None:
        self._lookback = lookback
        self._alpha = smoothing_alpha

    def forecast(self, history: PriceHistory | None) -> PriceForecast | None:
        """Forecast the next price for a product.

        Returns None if insufficient history.
        """
        if history is None or history.count() < 2:
            return None

        prices = history.prices_list()
        recent = prices[-self._lookback:] if len(prices) >= 2 else prices

        forecast_price = self._moving_average(recent)
        trend = self._detect_trend(prices)
        confidence = self._compute_confidence(len(prices), trend, recent)
        lower, upper = self._compute_bounds(recent, confidence)

        return PriceForecast(
            product=history.product,
            expected_price=forecast_price,
            confidence=confidence,
            lower_bound=lower,
            upper_bound=upper,
            trend=trend,
            method="moving_average",
        )

    def exponential_smooth(
        self, history: PriceHistory | None
    ) -> PriceForecast | None:
        """Forecast using exponential smoothing."""
        if history is None or history.count() < 2:
            return None

        prices = history.prices_list()
        if len(prices) < 2:
            return self.forecast(history)

        smoothed = prices[0]
        for p in prices[1:]:
            smoothed = self._alpha * p + (1 - self._alpha) * smoothed

        trend = self._detect_trend(prices)
        confidence = self._compute_confidence(len(prices), trend, prices)
        lower = smoothed * 0.8
        upper = smoothed * 1.2

        return PriceForecast(
            product=history.product,
            expected_price=smoothed,
            confidence=confidence,
            lower_bound=lower,
            upper_bound=upper,
            trend=trend,
            method="exponential_smoothing",
        )

    def _moving_average(self, prices: list[float]) -> float:
        if not prices:
            return 0.0
        return sum(prices) / len(prices)

    def _detect_trend(self, prices: list[float]) -> str:
        if len(prices) < 3:
            return "stable"

        recent = prices[-5:] if len(prices) >= 5 else prices
        first = recent[0]
        last = recent[-1]
        diff = last - first

        if abs(diff) < 0.5:
            return "stable"
        return "rising" if diff > 0 else "falling"

    def _compute_confidence(
        self, n: int, trend: str, prices: list[float]
    ) -> float:
        if not prices:
            return 0.0
        base = min(1.0, n / self._lookback)
        if trend == "stable":
            base *= 0.8
        else:
            base *= 0.6
        return max(0.1, min(1.0, base))

    def _compute_bounds(
        self, prices: list[float], confidence: float
    ) -> tuple[float, float]:
        if not prices:
            return 0.0, 0.0
        avg = sum(prices) / len(prices)
        volatility = max(prices) - min(prices)
        spread = volatility * (1.0 - confidence)
        return avg - spread, avg + spread
