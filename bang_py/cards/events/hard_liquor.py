from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HardLiquorEventCard(BaseEventCard):
    """Beer heals two health."""

    card_name = "Hard Liquor"
    description = "Beer heals 2"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["beer_heal"] = 2
