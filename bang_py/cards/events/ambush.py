from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class AmbushEventCard(BaseEventCard):
    """Set all player distances to 1 unless modified by other cards."""

    card_name = "Ambush"
    card_set = "fistful_of_cards"
    description = (
        "The distance between any two players is 1. "
        "Only other cards in play may modify this."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Ambush event."""
        if game:
            game.event_flags["ambush"] = True
