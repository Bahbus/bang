from __future__ import annotations

from .card import Card
from ..player import Player


class EquipmentCard(Card):
    """Base class for equipment cards."""

    card_name = "Equipment"
    slot: str | None = None
    # Range added to attacks made by the player
    range_modifier: int = 0
    # Distance penalty applied to opponents trying to target the player
    distance_modifier: int = 0
    # Optional description of the card's effect for UI purposes
    description: str | None = None
    # Green bordered cards activate on the owner's next turn
    green_border: bool = False

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        if self.green_border:
            self.active = False
        target.equip(self, active=self.active)
