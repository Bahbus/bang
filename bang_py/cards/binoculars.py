from __future__ import annotations

from .card import BaseCard
from ..player import Player


class BinocularsCard(BaseCard):
    """Blue card increasing your attack range by 1."""

    card_name = "Binoculars"
    card_type = "blue"
    card_set = "dodge_city"
    range_modifier = 1
    description = "Increases attack range by 1."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
