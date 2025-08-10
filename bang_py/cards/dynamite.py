"""Dynamite card from the base game. Start of turn draw may explode for 3 damage."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import is_spade_between

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck
    from ..game_manager_protocol import GameManagerProtocol


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

    @override
    def play(self, target: Player | None, deck: Deck | None = None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)

    @override
    def check_dynamite(self, gm: "GameManagerProtocol", player: Player) -> bool:
        """Resolve Dynamite at the start of ``player``'s turn.

        Returns ``True`` if it exploded on the current player.
        """
        if player.metadata.lucky_duke:
            c1 = gm._draw_from_deck()
            c2 = gm._draw_from_deck()
            card = c1 if not is_spade_between(c1, 2, 9) else c2
            if c1:
                gm.discard_pile.append(c1)
            if c2:
                gm.discard_pile.append(c2)
        else:
            card = gm._draw_from_deck()
            if card:
                gm.discard_pile.append(card)
        player.unequip(self.card_name)
        if is_spade_between(card, 2, 9):
            player.take_damage(3)
            return True
        next_player = gm._next_alive_player(player)
        if next_player:
            next_player.equip(self)
        return False
