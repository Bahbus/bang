from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class LawOfTheWestEventCard(BaseEventCard):
    """Second drawn card must be revealed and played if possible."""

    card_name = "Law of the West"
    card_set = "fistful_of_cards"
    description = "Play the second drawn card"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["law_of_the_west"] = True
