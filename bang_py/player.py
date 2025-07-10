from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .cards.equipment import EquipmentCard
    from .characters import Character


class Role(Enum):
    SHERIFF = auto()
    DEPUTY = auto()
    OUTLAW = auto()
    RENEGADE = auto()


@dataclass
class Player:
    name: str
    role: Role = Role.OUTLAW
    character: "Character | None" = None
    max_health: int = 4
    health: int = field(init=False)
    metadata: dict = field(default_factory=dict)
    equipment: Dict[str, "EquipmentCard"] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.health = self.max_health

    def equip(self, card: "EquipmentCard") -> None:
        """Add equipment to the player, respecting slot rules."""
        if getattr(card, "slot", None) == "Gun":
            self.equipment.pop("Gun", None)
            self.equipment["Gun"] = card
        else:
            # Replace any existing equipment with the same card name
            self.equipment[card.card_name] = card

    @property
    def gun_range(self) -> int:
        gun = self.equipment.get("Gun")
        if gun and hasattr(gun, "range"):
            return int(getattr(gun, "range"))
        return 1

    @property
    def range_bonus(self) -> int:
        """Bonus range from equipment such as Scope."""
        bonus = 0
        for eq in self.equipment.values():
            bonus += getattr(eq, "range_modifier", 0)
        if self.character is not None:
            bonus += getattr(self.character, "range_modifier", 0)
        return bonus

    @property
    def distance_bonus(self) -> int:
        """Distance penalty applied to opponents due to equipment such as Mustang."""
        bonus = 0
        for eq in self.equipment.values():
            bonus += getattr(eq, "distance_modifier", 0)
        if self.character is not None:
            bonus += getattr(self.character, "distance_modifier", 0)
        return bonus

    @property
    def attack_range(self) -> int:
        """Maximum range this player can target based on gun and equipment."""
        return self.gun_range + self.range_bonus

    def distance_to(self, other: "Player") -> int:
        """Calculate distance to another player considering equipment."""
        return max(1, 1 + other.distance_bonus - self.range_bonus)

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0

