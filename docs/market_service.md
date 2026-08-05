# Market Service

## Purpose

The market service manages market-related operations: tracking prices, processing orders, and analyzing supply/demand dynamics.

## Responsibilities

- Track current market inventory and prices
- Process buy/sell orders respecting `maxMarketOrdersPerTurn`
- Apply price shape functions (linear, sq, sqrt, log) per resource
- Enforce the floor price of 1
- Maintain historical price data

## Public Interfaces

### `MarketService`

```python
class MarketService:
    def process_orders(self, orders: list[MarketOrder], player_id: int) -> list[MarketResult]: ...
    def get_price(self, product: str) -> int: ...
    def update_inventory(self, product: str, delta: int) -> None: ...
```

### `MarketSnapshot`

A point-in-time capture of market state: inventory, prices, and timestamp.

### `MarketAnalyzer`

Analyzes trends, demand, supply, and historical values to inform strategy decisions.

## Extension Points

- Add new price shape functions in `domain/prices.py`.
- Extend `MarketAnalyzer` with forecasting capabilities.
- Add order prioritization logic in `MarketService`.