from agent.domain import inventory as inventory_domain


def test_inventory_defaults() -> None:
    inv = inventory_domain.Inventory()
    assert inv.items == {}
    assert inv.capacity == 100
