from __future__ import annotations

from .card import BaseCard
from ..player import Player


class RevCarabineCard(BaseCard):
    """Classic gun with range 4."""

    card_name = "Rev. Carabine"
    card_type = "equipment"
    card_set = "dodge_city"
    slot = "Gun"
    range = 4
    description = "Gun with range 4."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
