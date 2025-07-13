from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class BibleCard(Card):
    """Missed! effect that also lets the player draw a card."""

    card_name = "Bible"
    description = "Play as Missed! and then draw one card."
    green_border = True

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not target:
            return
        target.metadata.dodged = True
        if game:
            game.draw_card(player or target)
