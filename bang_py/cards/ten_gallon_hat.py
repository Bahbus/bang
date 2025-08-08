"""Ten Gallon Hat card from the Dodge City expansion. Counts as a Missed card."""

from __future__ import annotations

try:
    from typing import override
except ImportError:  # pragma: no cover - fallback for Python <3.12
    from typing_extensions import override

from .missed import MissedCard
from ..player import Player


class TenGallonHatCard(MissedCard):
    """Simple green-bordered Missed card."""

    card_name = "Ten Gallon Hat"
    card_type = "green"
    card_set = "dodge_city"
    description = "Counts as a Missed!"

    @override
    def play(self, target: Player | None, **kwargs) -> None:
        super().play(target, **kwargs)
