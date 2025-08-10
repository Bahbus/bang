"""The Sermon card from High Noon. Bang! cards cannot be played."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class TheSermonEventCard(BaseEventCard):
    """Bang! cards cannot be played."""

    card_name = "The Sermon"
    card_set = "high_noon"
    description = "Bang! cannot be played"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Sermon event."""
        if game:
            game.event_flags["no_bang"] = True
