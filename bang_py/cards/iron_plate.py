"""Iron Plate card from the Dodge City expansion. Counts as a Missed!"""

from __future__ import annotations

from .missed import MissedCard
from ..player import Player


class IronPlateCard(MissedCard):
    """Green bordered Missed card."""

    card_name = "Iron Plate"
    card_type = "green"
    card_set = "dodge_city"
    description = "Counts as a Missed!"

    def play(self, target: Player) -> None:  # type: ignore[override]
        super().play(target)
