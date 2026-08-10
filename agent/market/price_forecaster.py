from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from agent.market.price_tracker import PriceHistory


@dataclass
class PriceForecast:
    expected_price: float
    trend: str
    confidence: float
    lower_bound: float
    upper_bound: float
    method: str = "moving_average"
    product: str = ""


class PriceForecaster:
    """Simple price forecasting using moving averages and trend estimation.

    Only uses historical data that has already been observed at the time of
    the forecast (strict temporal causality).
    """

    def __init__(self, lookback: int = 5):
        self._lookback = lookback

    def forecast(self, history: PriceHistory) -> PriceForecast | None:
        prices = history.prices_list()
        if len(prices) < 2:
            return None
        recent = prices[-self._lookback :]
        expected_price = mean(recent)
        trend = self._detect_trend(prices)
        confidence = self._compute_confidence(prices)
        spread = self._spread(prices, confidence)
        return PriceForecast(
            expected_price=expected_price,
            trend=trend,
            confidence=confidence,
            lower_bound=max(1.0, expected_price - spread),
            upper_bound=expected_price + spread,
            method="moving_average",
            product=history.product,
        )

    def exponential_smooth(self, history: PriceHistory) -> PriceForecast | None:
        prices = history.prices_list()
        if len(prices) < 2:
            return None
        alpha = 0.4
        smoothed = prices[0]
        for price in prices[1:]:
            smoothed = alpha * price + (1.0 - alpha) * smoothed
        confidence = self._compute_confidence(prices)
        spread = self._spread(prices, confidence)
        return PriceForecast(
            expected_price=smoothed,
            trend=self._detect_trend(prices),
            confidence=confidence,
            lower_bound=max(1.0, smoothed - spread),
            upper_bound=smoothed + spread,
            method="exponential_smoothing",
            product=history.product,
        )

    def _detect_trend(self, prices: list[float]) -> str:
        if len(prices) < 2:
            return "stable"
        n = len(prices)
        x_mean = (n - 1) / 2.0
        y_mean = mean(prices)
        numerator = sum((i - x_mean) * (price - y_mean) for i, price in enumerate(prices))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator > 0 else 0.0
        scale = max(abs(y_mean), 1.0)
        if slope > 0.02 * scale:
            return "rising"
        if slope < -0.02 * scale:
            return "falling"
        return "stable"

    def _compute_confidence(self, prices: list[float]) -> float:
        if len(prices) < 2:
            return 0.5
        scale = max(abs(mean(prices)), 1.0)
        volatility = pstdev(prices) / scale
        return max(0.05, min(1.0, 1.0 - volatility))

    def _spread(self, prices: list[float], confidence: float) -> float:
        scale = max(abs(mean(prices)), 1.0)
        return max(pstdev(prices) if len(prices) > 1 else 0.0, (1.0 - confidence) * scale)
