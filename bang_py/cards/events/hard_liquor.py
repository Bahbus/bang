from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HardLiquorEventCard(BaseEventCard):
    """Players may skip their draw phase to heal 1 life."""

    card_name = "Hard Liquor"
    card_set = "fistful_of_cards"
    description = "Skip draw to heal 1"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Hard Liquor event."""
        if game:
            game.event_flags["hard_liquor"] = True
