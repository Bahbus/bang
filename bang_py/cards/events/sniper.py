from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class SniperEventCard(BaseEventCard):
    """Players may discard two Bang! cards as one attack."""

    card_name = "Sniper"
    description = "Play two Bang! cards together"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["sniper"] = True
