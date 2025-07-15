from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class ThirstEventCard(BaseEventCard):
    """Players draw only one card."""

    card_name = "Thirst"
    card_set = "high_noon"
    description = "Players draw only one card"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["draw_count"] = 1
