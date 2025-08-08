"""Jail card from the base game. Skip your turn unless you draw a Heart."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import is_heart

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck
    from ..game_manager_protocol import GameManagerProtocol


class JailCard(BaseCard):
    card_name = "Jail"
    card_type = "blue"
    description = "Skip your turn unless you draw a Heart."

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        super().__init__(suit, rank)
        self.active = True

    @override
    def play(self, target: Player | None, deck: Deck | None = None, **kwargs: Any) -> None:
        if not target:
            return
        target.equip(self, active=self.active)

    @override
    def check_turn(self, gm: "GameManagerProtocol", player: Player) -> bool:
        """Handle start-of-turn Jail check.

        Returns True if the player's turn is skipped.
        """
        if player.metadata.lucky_duke:
            card1 = gm._draw_from_deck()
            card2 = gm._draw_from_deck()
            chosen = card1 if is_heart(card1) or not is_heart(card2) else card2
            if card1:
                gm.discard_pile.append(card1)
            if card2:
                gm.discard_pile.append(card2)
            result = is_heart(chosen)
        else:
            card = gm._draw_from_deck()
            if card:
                gm.discard_pile.append(card)
            result = is_heart(card)
        player.unequip(self.card_name)
        return not result
