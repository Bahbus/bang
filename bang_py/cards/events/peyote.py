"""Peyote card from the Fistful of Cards expansion. During their draw phase, each player guesses red
or black. They reveal the top card; if correct they repeat until wrong."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class PeyoteEventCard(BaseEventCard):
    """Players guess red or black before each draw, repeating while correct."""

    card_name = "Peyote"
    card_set = "fistful_of_cards"
    description = (
        "During their draw phase, each player guesses red or black. They reveal the "
        "top card; if correct they repeat until wrong."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Peyote event."""
        if game:
            game.event_flags["peyote"] = True
