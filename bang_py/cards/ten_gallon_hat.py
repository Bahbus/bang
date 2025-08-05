"""Ten Gallon Hat card from the Dodge City expansion. Counts as a Missed!"""

from __future__ import annotations

from .missed import MissedCard
from ..player import Player


class TenGallonHatCard(MissedCard):
    """Simple green-bordered Missed card."""

    card_name = "Ten Gallon Hat"
    card_type = "green"
    card_set = "dodge_city"
    description = "Counts as a Missed!"

    def play(self, target: Player) -> None:  # type: ignore[override]
        super().play(target)
