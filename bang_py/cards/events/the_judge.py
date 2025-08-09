"""The Judge card from the Fistful of Cards expansion.

Players cannot play cards in front of themselves or others.
"""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class TheJudgeEventCard(BaseEventCard):
    """Players cannot play cards in front of themselves or others."""

    card_name = "The Judge"
    card_set = "fistful_of_cards"
    description = "Players cannot play cards in front of themselves or others."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Judge event."""
        if game:
            game.event_flags["judge"] = True
