from __future__ import annotations


class DomainEvent:
    pass


class CropPlanted(DomainEvent):
    __slots__ = ("crop_type", "day", "position")

    def __init__(self, position: tuple[int, int], crop_type: str, day: int) -> None:
        self.position = position
        self.crop_type = crop_type
        self.day = day


class CropHarvested(DomainEvent):
    __slots__ = ("crop_type", "day", "position", "yield_units")

    def __init__(
        self,
        position: tuple[int, int],
        crop_type: str,
        yield_units: int,
        day: int,
    ) -> None:
        self.position = position
        self.crop_type = crop_type
        self.yield_units = yield_units
        self.day = day


class AnimalFed(DomainEvent):
    __slots__ = ("animal_type", "day", "position")

    def __init__(self, position: tuple[int, int], animal_type: str, day: int) -> None:
        self.position = position
        self.animal_type = animal_type
        self.day = day


class ProductCollected(DomainEvent):
    __slots__ = ("day", "position", "product", "quantity")

    def __init__(self, position: tuple[int, int], product: str, quantity: int, day: int) -> None:
        self.position = position
        self.product = product
        self.quantity = quantity
        self.day = day


class WorkerAssigned(DomainEvent):
    __slots__ = ("day", "task", "worker_id")

    def __init__(self, worker_id: str, task: str, day: int) -> None:
        self.worker_id = worker_id
        self.task = task
        self.day = day


class MarketUpdated(DomainEvent):
    __slots__ = ("day", "new_price", "old_price", "product")

    def __init__(self, product: str, old_price: int, new_price: int, day: int) -> None:
        self.product = product
        self.old_price = old_price
        self.new_price = new_price
        self.day = day


class LandPurchased(DomainEvent):
    __slots__ = ("cost", "day", "quadrant")

    def __init__(self, quadrant: str, cost: int, day: int) -> None:
        self.quadrant = quadrant
        self.cost = cost
        self.day = day
