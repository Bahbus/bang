"""Missed! card from the base game. Negates one Bang! targeting you."""

from __future__ import annotations

from typing import override

from .card import BaseCard
from ..player import Player


class MissedCard(BaseCard):
    card_name = "Missed!"
    card_type = "action"
    card_set = "base"
    description = "Negates one Bang! targeting you."

    @override  # type: ignore[misc]
    def play(self, target: Player | None, **kwargs) -> None:
        if not target:
            return
        target.metadata.dodged = True
