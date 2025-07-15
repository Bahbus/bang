from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class PeyoteEventCard(BaseEventCard):
    """During their draw phase, each player guesses red or black. They reveal the top card; if correct they repeat until wrong."""

    card_name = "Peyote"
    card_set = "fistful_of_cards"
    description = "During their draw phase, each player guesses red or black. They reveal the top card; if correct they repeat until wrong."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["peyote"] = True
