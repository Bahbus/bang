from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheReverendEventCard(BaseEventCard):
    """Limit each player to two cards per turn."""

    card_name = "The Reverend"
    description = "Limit to two cards"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["reverend_limit"] = 2
