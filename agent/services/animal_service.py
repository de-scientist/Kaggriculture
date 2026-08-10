from __future__ import annotations

from typing import Any

from agent.domain.animal import Animal


def feed(animal: Animal) -> Animal:
    if not can_feed(animal):
        raise ValueError(f"Cannot feed {animal.animal_type} at current state")
    return animal.feed()


def collect(animal: Animal) -> tuple[Animal, int]:
    if not can_collect(animal):
        raise ValueError(f"Cannot collect from {animal.animal_type} at current state")
    return animal.produce()


def can_feed(animal: Animal) -> bool:
    return animal.is_alive and not animal.fed_today


def can_collect(animal: Animal) -> bool:
    return animal.is_alive and animal.fed_today


def expected_output(animal: Animal) -> dict[str, Any]:
    return {
        "animal_type": animal.animal_type,
        "fed_today": animal.fed_today,
        "cared_today": animal.cared_today,
        "pending_care_bonus": animal.pending_care_bonus,
        "is_alive": animal.is_alive,
    }


def production_status(animal: Animal) -> dict[str, Any]:
    return {
        "animal_type": animal.animal_type,
        "hunger": animal.hunger,
        "health": animal.health,
        "consecutive_unfed": animal.consecutive_unfed,
        "fed_today": animal.fed_today,
        "cared_today": animal.cared_today,
        "fertilizer_available": animal.fertilizer_available,
        "pending_care_bonus": animal.pending_care_bonus,
        "is_escaped": animal.is_escaped,
        "is_alive": animal.is_alive,
    }
