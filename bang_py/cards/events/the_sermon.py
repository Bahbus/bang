from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheSermonEventCard(BaseEventCard):
    """Bang! cards cannot be played."""

    card_name = "The Sermon"
    card_set = "high_noon"
    description = "Bang! cannot be played"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Sermon event."""
        if game:
            game.event_flags["no_bang"] = True
