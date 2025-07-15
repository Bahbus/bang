from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HandcuffsEventCard(BaseEventCard):
    """Limit each player to one suit per turn."""

    card_name = "Handcuffs"
    card_set = "high_noon"
    description = "Choose a suit after drawing"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["handcuffs"] = True
