"""Mustang card from the base game. Opponents see you at 1 greater distance."""

from __future__ import annotations
from typing import Any, override
from .card import BaseCard
from ..player import Player


class MustangCard(BaseCard):
    card_name = "Mustang"
    card_type = "blue"
    distance_modifier = 1
    description = "Opponents see you at 1 greater distance."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    @override
    def play(self, target: Player | None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
