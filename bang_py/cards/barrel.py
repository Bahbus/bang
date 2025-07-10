from __future__ import annotations

from .equipment import EquipmentCard
from ..player import Player


from typing import TYPE_CHECKING

from ..helpers import is_heart

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class BarrelCard(EquipmentCard):
    card_name = "Barrel"
    description = "Draw when targeted by Bang!; on Heart, ignore it."

    def play(self, target: Player, deck: Deck | None = None) -> None:
        super().play(target)

    def draw_check(self, deck: Deck) -> bool:
        """Perform the Barrel draw! check, returning True if Bang! is dodged."""
        card = deck.draw()
        return is_heart(card)
