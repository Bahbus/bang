from __future__ import annotations

from .card import BaseCard
from ..player import Player


from typing import TYPE_CHECKING

from ..helpers import is_heart

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class BarrelCard(BaseCard):
    card_name = "Barrel"
    card_type = "blue"
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
        gm = player.metadata.game if player else None
        if player and player.metadata.lucky_duke:
            card1 = deck.draw()
            card2 = deck.draw()
            chosen = card1 if is_heart(card1) or not is_heart(card2) else card2
            if gm:
                if card1:
                    gm.discard_pile.append(card1)
                if card2:
                    gm.discard_pile.append(card2)
            return is_heart(chosen)
        card = deck.draw()
        if gm and card:
            gm.discard_pile.append(card)
        return is_heart(card)
