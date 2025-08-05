"""High Noon card from the High Noon expansion. Lose 1 life at start of turn"""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HighNoonEventCard(BaseEventCard):
    """Players lose 1 life at the start of their turn."""

    card_name = "High Noon"
    card_set = "high_noon"
    description = "Lose 1 life at start of turn"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the High Noon event."""
        if game:
            game.event_flags["start_damage"] = 1
