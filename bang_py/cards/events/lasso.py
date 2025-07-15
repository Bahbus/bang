from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class LassoEventCard(BaseEventCard):
    """Cards in play in front of players have no effect."""

    card_name = "Lasso"
    card_set = "fistful_of_cards"
    description = "Cards in play in front of players have no effect."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["lasso"] = True
