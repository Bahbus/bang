from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class ShootoutEventCard(BaseEventCard):
    """Allow one extra Bang! per turn."""

    card_name = "Shootout"
    card_set = "high_noon"
    description = "Play two Bang!s"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["bang_limit"] = 2
