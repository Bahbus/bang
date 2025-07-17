from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class AbandonedMineEventCard(BaseEventCard):
    """Let players draw from the discard pile during the draw phase."""

    card_name = "Abandoned Mine"
    card_set = "fistful_of_cards"
    description = (
        "During draw, draw from discard pile if possible. "
        "Discards go face down on top of the deck."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Abandoned Mine event."""
        if game:
            game.event_flags["abandoned_mine"] = True
