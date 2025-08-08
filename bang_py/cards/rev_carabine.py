"""Rev. Carabine card from the Dodge City expansion. Gun with range 4."""

from __future__ import annotations
from typing import Any, override
from .card import BaseCard
from ..player import Player


class RevCarabineCard(BaseCard):
    """Classic gun with range 4."""

    card_name = "Rev. Carabine"
    card_type = "blue"
    card_set = "dodge_city"
    slot = "Gun"
    range = 4
    description = "Gun with range 4."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    @override
    def play(self, target: Player | None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
