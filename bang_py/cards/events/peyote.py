from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class PeyoteEventCard(BaseEventCard):
    """Players guess card color before drawing."""

    card_name = "Peyote"
    card_set = "fistful_of_cards"
    description = "Guess color before drawing"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["peyote"] = True
