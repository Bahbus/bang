"""Shootout card from the High Noon expansion. Each player may play a second Bang! card during their
turn."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class ShootoutEventCard(BaseEventCard):
    """Each player may play a second Bang! card during their turn."""

    card_name = "Shootout"
    card_set = "high_noon"
    description = "Each player may play a second Bang! card during their turn."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Shootout event."""
        if game:
            game.event_flags["bang_limit"] = 2
