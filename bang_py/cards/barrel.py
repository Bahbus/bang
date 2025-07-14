from __future__ import annotations

from .card import BaseCard
from ..player import Player


from typing import TYPE_CHECKING

from ..helpers import is_heart
from ..characters import LuckyDuke

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class BarrelCard(BaseCard):
    card_name = "Barrel"
    card_type = "equipment"
    description = "Draw when targeted by Bang!; on Heart, ignore it."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player, deck: Deck | None = None) -> None:
        if not target:
            return
        target.equip(self, active=self.active)

    def draw_check(self, deck: Deck, player: Player | None = None) -> bool:
        """Perform the Barrel draw! check, returning True if Bang! is dodged."""
        if player and isinstance(player.character, LuckyDuke):
            card1 = deck.draw()
            card2 = deck.draw()
            return is_heart(card1) or is_heart(card2)
        card = deck.draw()
        return is_heart(card)
