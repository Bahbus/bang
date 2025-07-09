from __future__ import annotations

from .card import Card
from ..player import Player


class BangCard(Card):
    card_name = "Bang!"

    def play(self, target: Player) -> None:
        if not target:
            return
        target.take_damage(1)

