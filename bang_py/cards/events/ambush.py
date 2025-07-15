from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class AmbushEventCard(BaseEventCard):
    """All players are at distance 1 from each other."""

    card_name = "Ambush"
    card_set = "fistful_of_cards"
    description = "Everyone distance 1"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["ambush"] = True
