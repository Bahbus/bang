from __future__ import annotations

from .card import BaseCard
from ..player import Player


class VolcanicCard(BaseCard):
    card_name = "Volcanic"
    card_type = "blue"
    slot = "Gun"
    range = 1
    # Allows the player to fire unlimited Bang! cards during their turn
    unlimited_bang = True
    description = "Gun with range 1. Allows unlimited Bang! cards per turn."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
