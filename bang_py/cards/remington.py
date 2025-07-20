from __future__ import annotations

from .card import BaseCard
from ..player import Player


class RemingtonCard(BaseCard):
    card_name = "Remington"
    card_type = "blue"
    slot = "Gun"
    range = 3
    description = "Gun with range 3."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
