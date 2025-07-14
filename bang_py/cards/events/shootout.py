from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class ShootoutEventCard(BaseEventCard):
    """Allow unlimited Bang! cards this turn."""

    card_name = "Shootout"
    description = "Unlimited Bang!s per turn"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["bang_limit"] = 99
