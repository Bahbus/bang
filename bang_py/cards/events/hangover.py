from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HangoverEventCard(BaseEventCard):
    """All characters temporarily lose their abilities."""

    card_name = "Hangover"
    card_set = "high_noon"
    description = "All characters lose their abilities."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Hangover event."""
        if game:
            game.event_flags["no_abilities"] = True
