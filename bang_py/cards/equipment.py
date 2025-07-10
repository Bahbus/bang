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

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self)
