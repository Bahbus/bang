from __future__ import annotations

from .missed import MissedCard
from ..player import Player


class SombreroCard(MissedCard):
    """Simple green-bordered Missed card."""

    card_name = "Sombrero"
    card_type = "green"
    card_set = "dodge_city"
    description = "Counts as a Missed!"

    def play(self, target: Player) -> None:  # type: ignore[override]
        super().play(target)
