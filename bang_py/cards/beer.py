from __future__ import annotations

from .card import Card
from ..player import Player


class BeerCard(Card):
    card_name = "Beer"

    def play(self, target: Player) -> None:
        if not target:
            return
        target.heal(1)

