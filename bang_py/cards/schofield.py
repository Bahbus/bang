"""Schofield card from the base game. Gun with range 2."""

from __future__ import annotations

from .card import BaseCard
from ..player import Player


class SchofieldCard(BaseCard):
    card_name = "Schofield"
    card_type = "blue"
    slot = "Gun"
    range = 2
    description = "Gun with range 2."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
