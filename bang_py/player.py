from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto


class Role(Enum):
    SHERIFF = auto()
    DEPUTY = auto()
    OUTLAW = auto()
    RENEGADE = auto()


@dataclass
class Player:
    name: str
    role: Role = Role.OUTLAW
    max_health: int = 4
    health: int = field(init=False)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.health = self.max_health

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0

