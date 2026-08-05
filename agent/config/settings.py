from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Settings:
    environment: str = "development"
    game: Dict[str, Any] = field(default_factory=dict)
    market: Dict[str, Any] = field(default_factory=dict)
    town: Dict[str, Any] = field(default_factory=dict)
    logging: Dict[str, Any] = field(default_factory=dict)
    strategy: Dict[str, Any] = field(default_factory=dict)