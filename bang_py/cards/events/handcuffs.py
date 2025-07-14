from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HandcuffsEventCard(BaseEventCard):
    """Skip the next player's turn."""

    card_name = "Handcuffs"
    description = "Skip the sheriff's turn"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["skip_turn"] = True
