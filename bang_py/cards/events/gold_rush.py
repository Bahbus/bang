from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class GoldRushEventCard(BaseEventCard):
    """Reverse player order while card effects remain clockwise."""

    card_name = "Gold Rush"
    card_set = "high_noon"
    description = "The game proceeds counter-clockwise, but card effects still proceed clockwise."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Gold Rush event."""
        if game:
            game.event_flags["reverse_turn"] = True
