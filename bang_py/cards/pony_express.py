from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class PonyExpressCard(Card):
    """Draw three cards."""

    card_name = "Pony Express"
    description = "Draw three cards."
    green_border = True

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if player and game:
            game.draw_card(player, 3)
