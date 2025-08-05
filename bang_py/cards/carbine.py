"""Carbine card from the base game. Gun with range 4."""

from __future__ import annotations

from .card import BaseCard
from ..player import Player


class CarbineCard(BaseCard):
    card_name = "Carbine"
    card_type = "blue"
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
