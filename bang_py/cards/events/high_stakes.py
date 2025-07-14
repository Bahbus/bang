from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HighStakesEventCard(BaseEventCard):
    """Players may play any number of Bang! cards."""

    card_name = "High Stakes"
    description = "Players may play any number of Bang! cards"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["bang_limit"] = 99
