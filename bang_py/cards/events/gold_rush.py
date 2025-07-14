from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class GoldRushEventCard(BaseEventCard):
    """Players draw three cards each draw phase."""

    card_name = "Gold Rush"
    description = "Draw three cards"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["draw_count"] = 3
