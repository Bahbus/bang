from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..deck import Deck
    from ..game_manager import GameManager


class StagecoachCard(Card):
    card_name = "Stagecoach"
    description = "Draw two cards."

    def play(
        self, target: Player, game: GameManager | None = None, deck: Deck | None = None
    ) -> None:
        if game:
            game.draw_card(target, 2)
        elif deck:
            for _ in range(2):
                card = deck.draw()
                if card:
                    target.hand.append(card)
