from __future__ import annotations

from .card import Card
from ..player import Player


class MissedCard(Card):
    card_name = "Missed!"

    def play(self, target: Player) -> None:
        if not target:
            return
        target.metadata["dodged"] = True

