"""Gold Rush card from High Noon. Turn order goes counter-clockwise, effects resolve clockwise."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class GoldRushEventCard(BaseEventCard):
    """Reverse player order while card effects remain clockwise."""

    card_name = "Gold Rush"
    card_set = "high_noon"
    description = "The game proceeds counter-clockwise, but card effects still proceed clockwise."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Gold Rush event."""
        if game:
            game.event_flags["reverse_turn"] = True
