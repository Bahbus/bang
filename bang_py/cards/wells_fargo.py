"""Wells Fargo card from the base game. Draw three cards."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..deck import Deck
    from ..game_manager import GameManager


class WellsFargoCard(BaseCard):
    card_name = "Wells Fargo"
    card_type = "action"
    card_set = "base"
    description = "Draw three cards."

    @override
    def play(
        self,
        target: Player | None,
        game: GameManager | None = None,
        deck: Deck | None = None,
        **kwargs: Any,
    ) -> None:
        if not target:
            return
        if game:
            game.draw_card(target, 3)
        elif deck:
            for _ in range(3):
                card = deck.draw()
                if card:
                    target.hand.append(card)
