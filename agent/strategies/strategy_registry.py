from __future__ import annotations

from agent.strategies.strategy import Strategy


_REGISTRY: dict[str, type[Strategy]] = {}


def register(name: str, cls: type[Strategy]) -> None:
    if not issubclass(cls, Strategy):
        raise TypeError(f"{cls} is not a Strategy subclass")
    _REGISTRY[name] = cls


def get(name: str) -> type[Strategy] | None:
    return _REGISTRY.get(name)


def is_registered(name: str) -> bool:
    return name in _REGISTRY


def names() -> list[str]:
    return list(_REGISTRY.keys())


def validate(name: str) -> bool:
    cls = _REGISTRY.get(name)
    if cls is None:
        return False
    return issubclass(cls, Strategy)