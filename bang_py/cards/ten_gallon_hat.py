from __future__ import annotations

from .missed import MissedCard
from ..player import Player


class TenGallonHatCard(MissedCard):
    """Simple green-bordered Missed!"""

    card_name = "Ten Gallon Hat"
    description = "Counts as a Missed!"
    green_border = True

    def play(self, target: Player) -> None:  # type: ignore[override]
        super().play(target)
