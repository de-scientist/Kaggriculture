"""Unit tests for Price Forecaster (Stage 2)."""

from __future__ import annotations

from agent.market.price_forecaster import PriceForecaster
from agent.market.price_tracker import PriceHistory, PriceSnapshot


class TestPriceForecaster:
    def test_forecast_insufficient_data(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        result = forecaster.forecast(history)
        assert result is None  # need at least 2 data points

    def test_forecast_single_point(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        history.add(PriceSnapshot(turn=0, product="WHEAT", price=10.0, inventory=20))
        result = forecaster.forecast(history)
        assert result is None  # need at least 2

    def test_forecast_stable_prices(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        for i in range(5):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=10.0, inventory=20))
        result = forecaster.forecast(history)
        assert result is not None
        assert result.trend == "stable"
        assert result.expected_price == 10.0

    def test_forecast_rising_prices(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        for i in range(6):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=10 + i, inventory=20 - i))
        result = forecaster.forecast(history)
        assert result is not None
        assert result.trend == "rising"

    def test_forecast_falling_prices(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        for i in range(6):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=20 - i, inventory=20 + i))
        result = forecaster.forecast(history)
        assert result is not None
        assert result.trend == "falling"

    def test_exponential_smooth(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        for i in range(6):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=float(i + 1), inventory=20))
        result = forecaster.exponential_smooth(history)
        assert result is not None
        assert result.method == "exponential_smoothing"

    def test_confidence_decreases_with_volatility(self) -> None:
        forecaster = PriceForecaster(lookback=5)
        history = PriceHistory(product="WHEAT")
        # Stable prices
        for i in range(5):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=10.0, inventory=20))
        stable_result = forecaster.forecast(history)

        history2 = PriceHistory(product="WHEAT")
        # Volatile prices
        for i in range(5):
            history2.add(
                PriceSnapshot(turn=i, product="WHEAT", price=float(10 + i * 5), inventory=20)
            )
        volatile_result = forecaster.forecast(history2)

        assert volatile_result is not None
        assert stable_result is not None
        assert volatile_result.confidence <= stable_result.confidence

    def test_bounds_contain_expected(self) -> None:
        forecaster = PriceForecaster()
        history = PriceHistory(product="WHEAT")
        for i in range(10):
            history.add(PriceSnapshot(turn=i, product="WHEAT", price=10.0, inventory=20))
        result = forecaster.forecast(history)
        assert result is not None
        assert result.lower_bound <= result.expected_price <= result.upper_bound
