from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, TYPE_CHECKING

from .characters import BelleStar

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .cards.equipment import EquipmentCard
    from .characters import Character
    from .cards.card import Card


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
    hand: List["Card"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize max health from role and character modifiers."""
        base = 5 if self.role == Role.SHERIFF else 4
        self.max_health = base
        if self.character is not None:
            bonus = getattr(self.character, "max_health_modifier", 0)
            self.max_health += int(bonus)
        self.health = self.max_health

    def _apply_health_modifier(self, amount: int) -> None:
        """Adjust max and current health by a modifier."""
        self.max_health += amount
        if amount > 0:
            self.health += amount
        else:
            self.health = min(self.health, self.max_health)

    def equip(self, card: "EquipmentCard") -> None:
        """Add equipment to the player, respecting slot rules."""
        existing = None
        if getattr(card, "slot", None) == "Gun":
            existing = self.equipment.pop("Gun", None)
            self.equipment["Gun"] = card
        else:
            existing = self.equipment.pop(card.card_name, None)
            self.equipment[card.card_name] = card

        if existing:
            self._apply_health_modifier(
                -int(getattr(existing, "max_health_modifier", 0))
            )

        modifier = int(getattr(card, "max_health_modifier", 0))
        if modifier:
            self._apply_health_modifier(modifier)

    def unequip(self, card_name: str) -> "EquipmentCard | None":
        """Remove equipment by name and adjust health if needed."""
        card = self.equipment.pop(card_name, None)
        if card:
            modifier = int(getattr(card, "max_health_modifier", 0))
            if modifier:
                self._apply_health_modifier(-modifier)
        return card

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
        """Return distance to another player considering equipment and abilities."""
        game = self.metadata.get("game")
        players = getattr(game, "players", None)

        base = 1
        if players and self in players and other in players:
            base = self._seated_distance(self, other, players)

        ignore_other_bonus = False
        if game and game.turn_order:
            current = game.players[game.turn_order[game.current_turn % len(game.turn_order)]]
            if current is self and isinstance(getattr(self, "character", None), BelleStar):
                ignore_other_bonus = True

        distance = base + (0 if ignore_other_bonus else other.distance_bonus) - self.range_bonus
        return max(1, distance)

    @staticmethod
    def _seated_distance(player: "Player", other: "Player", players: List["Player"]) -> int:
        """Return the seat distance between two players counting only the living."""

        alive = [p for p in players if p.is_alive()]
        p_index = alive.index(player)
        o_index = alive.index(other)
        diff = abs(p_index - o_index)
        return min(diff, len(alive) - diff)

    def take_damage(self, amount: int) -> None:
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0

