import math
from typing import Dict, Any


class PriceModel:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.I0 = 10000
        self.price_floor = 1

    def predict(self, item: str, inventory: Dict[str, int], horizon: int = 0) -> int:
        params = self._get_item_params(item)
        current_inv = inventory.get(item, 0)
        if horizon > 0:
            current_inv += horizon * self._get_average_daily_change(item)
        price = self._calculate_price(params, current_inv)
        return max(self.price_floor, round(price))

    def _get_item_params(self, item: str) -> Dict[str, Any]:
        default_params = {
            "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.8, "above_func": "log", "above_target": 0.2},
            "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "log", "below_target": 0.2, "above_func": "sqrt", "above_target": 0.7},
            "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.4, "above_func": "sqrt", "above_target": 0.6},
            "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.7, "above_func": "linear", "above_target": 1.6},
            "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.2, "above_func": "sq", "above_target": 3.6},
            "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "linear", "below_target": 0.4, "above_func": "log", "above_target": 0.2},
            "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.6, "above_func": "linear", "above_target": 1.6},
            "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.2, "above_func": "sq", "above_target": 3.2},
            "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.4, "above_func": "linear", "above_target": 0.4},
        }
        if item in self.config.get("marketParams", {}):
            params = {**default_params.get(item, {}), **self.config["marketParams"][item]}
        else:
            params = default_params.get(item, {})
        return params

    def _calculate_price(self, params: Dict[str, Any], inventory: int) -> float:
        base = params.get("base", 0)
        I0 = params.get("I0", 10000)
        if inventory < I0:
            sign = 1
        else:
            sign = -1
        diff = abs(inventory - I0)
        shape = self._get_shape_function(params, sign)
        amp = self._calculate_amp(params)
        adjustment = amp * shape(diff)
        return base + sign * adjustment

    def _get_shape_function(self, params: Dict[str, Any], sign: int) -> callable:
        if sign > 0:
            func_name = params.get("below_func", "linear")
        else:
            func_name = params.get("above_func", "linear")
        shapes = {
            "linear": lambda x: x,
            "sq": lambda x: x * x,
            "sqrt": lambda x: math.sqrt(x) if x >= 0 else 0,
            "log": lambda x: math.log(1 + x) if x >= 0 else 0,
            "log10": lambda x: math.log10(1 + x) if x >= 0 else 0,
        }
        return shapes.get(func_name, lambda x: x)

    def _calculate_amp(self, params: Dict[str, Any]) -> float:
        target = params.get("below_target" if True else "above_target", 1.0)
        base = params.get("base", 0)
        T = params.get("T", 1000)
        fT = self._get_shape_function(params, 1)(T)
        if fT > 0:
            return target * base / fT
        return 0

    def _get_average_daily_change(self, item: str) -> float:
        return -1.0