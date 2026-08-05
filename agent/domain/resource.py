from dataclasses import dataclass


@dataclass
class Resource:
    name: str = ""
    amount: int = 0