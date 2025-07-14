from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheDaltonsEventCard(BaseEventCard):
    """Each player draws a card."""

    card_name = "The Daltons"
    description = "Everyone draws"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in game.players:
            game.draw_card(p)
