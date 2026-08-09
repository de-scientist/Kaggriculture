from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent.market.price_tracker import PriceTracker


@dataclass
class PriceForecast:
    predicted_price: float
    confidence: float
    predicted_range: tuple[float, float]
    forecast_date: str


class PriceForecaster:
    """Simple price forecasting using moving average and trend estimation."""

    def __init__(self):
        self._window = 5
        self._trend_window = 10

    def forecast(
        self,
        current_prices: dict[str, int],
        history: dict[str, list[float]],
    ) -> dict[str, PriceForecast]:
        forecasts: dict[str, PriceForecast] = {}
        for product, current_price in current_prices.items():
            hist = history.get(product, [])
            if len(hist) < 2:
                forecasts[product] = PriceForecast(
                    predicted_price=float(current_price),
                    confidence=0.5,
                    predicted_range=(float(current_price) - 1, float(current_price) + 1),
                    forecast_date="unknown",
                )
                continue

            recent = hist[-self._window:]
            if len(recent) < 2:
                forecasts[product] = PriceForecast(
                    predicted_price=float(current_price),
                    confidence=0.5,
                    predicted_range=(float(current_price) - 1, float(current_price) + 1),
                    forecast_date="unknown",
                )
                continue

            moving_avg = sum(recent) / len(recent)
            trend = sum(hist[-self._trend_window:]) / min(len(hist), self._trend_window) - moving_avg

            predicted = float(moving_avg) + trend * 0.5
            confidence = self._compute_confidence(hist)
            predicted_range = (
                max(1.0, predicted - 2.0 * confidence),
                predicted + 2.0 * confidence,
            )

            forecasts[product] = PriceForecast(
                predicted_price=round(predicted, 1),
                confidence=confidence,
                predicted_range=(round(predicted_range[0], 1), round(predicted_range[1], 1)),
                forecast_date="current",
            )

        return forecasts

    def _compute_confidence(self, history: list[float]) -> float:
        if len(history) < 5:
            return 0.5
        recent = history[-10:]
        avg = sum(recent) / len(recent)
        variance = sum((x - avg) ** 2 for x in recent) / len(recent)
        return max(0.0, min(1.0, 1.0 - variance / 100.0))

    def update_history(
        self,
        product: str,
        new_price: int,
        history: list[float],
    ) -> list[float]:
        history.append(float(new_price))
        return history[-20:]