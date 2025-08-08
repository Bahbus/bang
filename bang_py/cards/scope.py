"""Scope card from the base game. Increases your attack range by 1."""

from __future__ import annotations
from typing import Any, override
from .card import BaseCard
from ..player import Player


class ScopeCard(BaseCard):
    card_name = "Scope"
    card_type = "blue"
    range_modifier = 1
    description = "Increases your attack range by 1."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    @override
    def play(self, target: Player | None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)
