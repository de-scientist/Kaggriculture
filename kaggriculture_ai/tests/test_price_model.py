import pytest
from kaggriculture_ai.economy.price_model import PriceModel


def test_price_model_basic():
    config = {}
    model = PriceModel(config)
    price = model.predict("WHEAT", {"WHEAT": 10000})
    assert price == 25


def test_price_model_scarcity():
    config = {}
    model = PriceModel(config)
    price = model.predict("WHEAT", {"WHEAT": 5000})
    assert price > 25


def test_price_model_glut():
    config = {}
    model = PriceModel(config)
    price = model.predict("WHEAT", {"WHEAT": 15000})
    assert price < 25