"""Blessing card from High Noon. Treat all cards as Hearts."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class BlessingEventCard(BaseEventCard):
    """Treat the suit of all cards as Hearts."""

    card_name = "Blessing"
    card_set = "high_noon"
    description = "All cards are Hearts"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Blessing event."""
        if game:
            game.event_flags["suit_override"] = "Hearts"
