from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HandcuffsEventCard(BaseEventCard):
    """Players choose one suit to play after drawing."""

    card_name = "Handcuffs"
    card_set = "high_noon"
    description = (
        "After their draw phase, each player announces a suit and can only play "
        "that suit for the rest of their turn."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Handcuffs event."""
        if game:
            game.event_flags["handcuffs"] = True
