from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class CurseEventCard(BaseEventCard):
    """Treat the suit of all cards as Spades."""

    card_name = "Curse"
    card_set = "high_noon"
    description = "All cards are Spades"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["suit_override"] = "Spades"
