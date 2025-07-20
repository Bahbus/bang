from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_spade_between

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class DynamiteCard(BaseCard):
    card_name = "Dynamite"
    card_type = "blue"
    description = (
        "Passes around; at the start of your turn draw a card, and if it is a "
        "spade between 2 and 9, Dynamite explodes for 3 damage."
    )

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    def play(self, target: Player, deck: Deck | None = None) -> None:
        if not target:
            return
        target.equip(self, active=self.active)

    def check_dynamite(
        self, current: Player, next_player: Player, deck: Deck
    ) -> bool:
        """Resolve Dynamite at the start of the current player's turn.

        Returns True if it exploded on the current player.
        """
        gm = current.metadata.game
        if current.metadata.lucky_duke:
            c1 = deck.draw()
            c2 = deck.draw()
            card = c1 if not is_spade_between(c1, 2, 9) else c2
            if gm:
                if c1:
                    gm.discard_pile.append(c1)
                if c2:
                    gm.discard_pile.append(c2)
        else:
            card = deck.draw()
            if gm and card:
                gm.discard_pile.append(card)
        current.unequip(self.card_name)
        if is_spade_between(card, 2, 9):
            current.take_damage(3)
            return True
        next_player.equip(self)
        return False
