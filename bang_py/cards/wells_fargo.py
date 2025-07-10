from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..deck import Deck
    from ..game_manager import GameManager


class WellsFargoCard(Card):
    card_name = "Wells Fargo"

    def play(
        self, target: Player, game: GameManager | None = None, deck: Deck | None = None
    ) -> None:
        if game:
            game.draw_card(target, 3)
        elif deck:
            for _ in range(3):
                card = deck.draw()
                if card:
                    target.hand.append(card)
