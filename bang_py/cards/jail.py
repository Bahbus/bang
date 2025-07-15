from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_heart

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class JailCard(BaseCard):
    card_name = "Jail"
    card_type = "equipment"
    description = "Skip your turn unless you draw a Heart."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player, deck: Deck | None = None) -> None:
        if not target:
            return
        target.equip(self, active=self.active)

    def check_turn(self, player: Player, deck: Deck) -> bool:
        """Handle start-of-turn Jail check.

        Returns True if the player's turn is skipped.
        """
        gm = player.metadata.game
        if player.metadata.lucky_duke:
            card1 = deck.draw()
            card2 = deck.draw()
            chosen = card1 if is_heart(card1) or not is_heart(card2) else card2
            if gm:
                if card1:
                    gm.discard_pile.append(card1)
                if card2:
                    gm.discard_pile.append(card2)
            result = is_heart(chosen)
        else:
            card = deck.draw()
            if gm and card:
                gm.discard_pile.append(card)
            result = is_heart(card)
        player.unequip(self.card_name)
        return not result
