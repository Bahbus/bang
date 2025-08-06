"""Player representation and related helper data for Bang."""

from __future__ import annotations
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Sequence, TYPE_CHECKING

from .cards.roles import (
    BaseRole,
    OutlawRoleCard,
    SheriffRoleCard,
)


if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .characters.base import BaseCharacter
    from .cards.card import BaseCard
    from .game_manager import GameManager


@dataclass(slots=True)
class PlayerMetadata:
    """State information associated with a player."""

    game: "GameManager | None" = None
    auto_miss: bool = True
    awaiting_draw: bool = False
    bangs_played: int = 0
    doc_free_bang: int = 0
    doc_used: bool = False
    dodged: bool = False
    ghost_revived: bool = False
    kit_cards: list["BaseCard"] | None = None
    lucky_cards: list["BaseCard"] | None = None
    gringo_index: int | None = None
    uncle_used: bool = False
    vera_copy: type["BaseCharacter"] | None = None
    unused_character: "BaseCharacter | None" = None
    abilities: set[type["BaseCharacter"]] = field(default_factory=set)
    hand_limit: int | None = None
    # ability flags
    ignore_others_equipment: bool = False
    unlimited_bang: bool = False
    no_hand_limit: bool = False
    double_miss: bool = False
    draw_when_empty: bool = False
    immune_diamond: bool = False
    play_missed_as_bang: bool = False
    bang_as_missed: bool = False
    any_card_as_missed: bool = False
    lucky_duke: bool = False
    virtual_barrel: bool = False
    use_sniper: bool = False
    beer_heal_bonus: int = 0


@dataclass(slots=True)
class Player:
    name: str
    role: BaseRole | None = None
    character: "BaseCharacter | None" = None
    max_health: int = 4
    _health: int = field(init=False, repr=False)
    _metadata: PlayerMetadata = field(default_factory=PlayerMetadata, init=False, repr=False)
    _equipment: dict[str, "BaseCard"] = field(default_factory=dict, init=False, repr=False)
    hand: list["BaseCard"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize max health from role and character."""
        self.reset_stats()

    @property
    def metadata(self) -> PlayerMetadata:
        """Player metadata (read-only reference)."""
        return self._metadata

    @property
    def equipment(self) -> dict[str, "BaseCard"]:
        """Mapping of currently equipped cards (read-only)."""
        return MappingProxyType(self._equipment)

    @property
    def health(self) -> int:
        """Current health points."""
        return self._health

    @health.setter
    def health(self, value: int) -> None:
        """Set current health clamping between 0 and ``max_health``."""
        self._health = max(0, min(value, self.max_health))

    def reset_stats(self) -> None:
        """Recalculate health and abilities after assigning role or character."""
        base = 4
        if self.character is not None:
            base = getattr(self.character, "starting_health", 4)
        if isinstance(self.role, SheriffRoleCard):
            base += 1
        self.max_health = base
        self.health = base
        self.metadata.abilities.clear()
        if self.character is not None:
            self.metadata.abilities.add(self.character.__class__)

    def _apply_health_modifier(self, amount: int) -> None:
        """Adjust max and current health by a modifier."""
        self.max_health += amount
        if amount > 0:
            self.health += amount
        else:
            self.health = min(self.health, self.max_health)

    def equip(self, card: "BaseCard", *, active: bool = True) -> None:
        """Add equipment to the player, respecting slot rules."""
        existing = None
        if getattr(card, "slot", None) == "Gun":
            existing = self._equipment.pop("Gun", None)
            self._equipment["Gun"] = card
        else:
            existing = self._equipment.pop(card.card_name, None)
            self._equipment[card.card_name] = card

        if existing:
            modifier = int(getattr(existing, "max_health_modifier", 0))
            if modifier and getattr(existing, "active", True):
                self._apply_health_modifier(-modifier)

        card.active = active
        if active:
            modifier = int(getattr(card, "max_health_modifier", 0))
            if modifier:
                self._apply_health_modifier(modifier)

    def unequip(self, card_name: str) -> "BaseCard | None":
        """Remove equipment by name and adjust health if needed."""
        card = self._equipment.pop(card_name, None)
        if card:
            modifier = int(getattr(card, "max_health_modifier", 0))
            if modifier and getattr(card, "active", True):
                self._apply_health_modifier(-modifier)
        return card

    @property
    def gun_range(self) -> int:
        """Return the base firing range provided by the equipped gun."""
        game = self.metadata.game
        if getattr(game, "event_flags", {}).get("lasso"):
            return 1
        gun = self._equipment.get("Gun")
        if gun and hasattr(gun, "range") and getattr(gun, "active", True):
            return int(getattr(gun, "range"))
        return 1

    @property
    def range_bonus(self) -> int:
        """Bonus range from equipment such as Scope."""
        bonus = 0
        game = self.metadata.game
        ignore = getattr(game, "event_flags", {}).get("lasso")
        for eq in self._equipment.values():
            if not ignore and getattr(eq, "active", True):
                bonus += getattr(eq, "range_modifier", 0)
        if self.character is not None:
            bonus += getattr(self.character, "range_modifier", 0)
        return bonus

    @property
    def distance_bonus(self) -> int:
        """Distance penalty applied to opponents due to equipment such as Mustang."""
        bonus = 0
        game = self.metadata.game
        ignore = getattr(game, "event_flags", {}).get("lasso")
        for eq in self._equipment.values():
            if not ignore and getattr(eq, "active", True):
                bonus += getattr(eq, "distance_modifier", 0)
        if self.character is not None:
            bonus += getattr(self.character, "distance_modifier", 0)
        return bonus

    @property
    def attack_range(self) -> int:
        """Maximum range this player can target based on gun and equipment."""
        game = self.metadata.game
        if getattr(game, "event_flags", {}).get("range_unlimited"):
            return 99
        rng = self.gun_range + self.range_bonus
        if (
            getattr(game, "event_flags", {}).get("vendetta")
            and isinstance(self.role, OutlawRoleCard)
        ):
            rng += 1
        return rng

    def distance_to(self, other: "Player") -> int:
        """Return distance to another player considering equipment and abilities."""
        game = self.metadata.game
        players = getattr(game, "players", None)

        base = 1
        if players and self in players and other in players:
            base = self._seated_distance(self, other, players)
        if getattr(game, "event_flags", {}).get("ambush"):
            base = 1

        ignore_other_bonus = False
        if game and game.turn_order:
            current = game.players[game.turn_order[game.current_turn % len(game.turn_order)]]
            if current is self and current.metadata.ignore_others_equipment:
                ignore_other_bonus = True

        distance = base + (0 if ignore_other_bonus else other.distance_bonus) - self.range_bonus
        return max(1, distance)

    @staticmethod
    def _seated_distance(player: "Player", other: "Player", players: Sequence["Player"]) -> int:
        """Return the seat distance between two players counting only the living."""
        alive = [p for p in players if p.is_alive()]
        p_index = alive.index(player)
        o_index = alive.index(other)
        diff = abs(p_index - o_index)
        return min(diff, len(alive) - diff)

    def take_damage(self, amount: int) -> None:
        """Decrease health but not below zero."""
        self.health = max(0, self.health - amount)

    def heal(self, amount: int) -> None:
        """Restore health up to ``max_health``."""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        """Return ``True`` if the player still has health remaining."""
        return self.health > 0
