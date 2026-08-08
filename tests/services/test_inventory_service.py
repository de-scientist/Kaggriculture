from agent.domain.inventory import Inventory
from agent.services import inventory_service


def test_add_item():
    inv = Inventory()
    result = inventory_service.add(inv, "WHEAT", 5)
    assert inventory_service.available(result, "WHEAT") == 5


def test_remove_item():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    result = inventory_service.remove(with_inv, "WHEAT", 3)
    assert inventory_service.available(result, "WHEAT") == 2


def test_remove_item_insufficient_raises():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 2)
    try:
        inventory_service.remove(with_inv, "WHEAT", 5)
        raise AssertionError("Should have raised ValueError")
    except ValueError:
        pass


def test_reserve_item():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    result = inventory_service.reserve(with_inv, "WHEAT", 2)
    assert inventory_service.available(result, "WHEAT") == 3


def test_release_item():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    reserved = inventory_service.reserve(with_inv, "WHEAT", 2)
    result = inventory_service.release(reserved, "WHEAT", 2)
    assert inventory_service.available(result, "WHEAT") == 5


def test_available():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    assert inventory_service.available(with_inv, "WHEAT") == 5
    assert inventory_service.available(with_inv, "CARROT") == 0


def test_capacity_remaining():
    inv = Inventory(capacity=10)
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    assert inventory_service.capacity_remaining(with_inv) == 5


def test_contains():
    inv = Inventory()
    with_inv = inventory_service.add(inv, "WHEAT", 5)
    assert inventory_service.contains(with_inv, "WHEAT", 3) is True
    assert inventory_service.contains(with_inv, "WHEAT", 6) is False
