"""Hideout card from the Dodge City expansion. Opponents see you at +1 distance."""

from __future__ import annotations
from typing import Any, override
from .card import BaseCard
from ..player import Player


class HideoutCard(BaseCard):
    """Blue card increasing distance others see you by 1."""

    card_name = "Hideout"
    card_type = "blue"
    card_set = "dodge_city"
    distance_modifier = 1
    description = "Opponents see you at +1 distance."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    @override
    def play(self, target: Player | None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
