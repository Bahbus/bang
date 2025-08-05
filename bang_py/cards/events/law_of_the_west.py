"""Law of the West card from the Fistful of Cards expansion. During their draw phase, each player
must reveal the second card they drew and play it immediately if possible."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class LawOfTheWestEventCard(BaseEventCard):
    """Players reveal and immediately play their second drawn card."""

    card_name = "Law of the West"
    card_set = "fistful_of_cards"
    description = (
        "During their draw phase, each player must reveal the second card they drew "
        "and play it immediately if possible."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Law of the West event."""
        if game:
            game.event_flags["law_of_the_west"] = True
