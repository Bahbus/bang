from __future__ import annotations

from .card import BaseCard
from ..player import Player


class MissedCard(BaseCard):
    card_name = "Missed!"
    card_type = "action"
    card_set = "base"
    description = "Negates one Bang! targeting you."

    def play(self, target: Player) -> None:
        if not target:
            return
        target.metadata.dodged = True
