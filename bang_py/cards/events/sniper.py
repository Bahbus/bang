from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class SniperEventCard(BaseEventCard):
    """Discard two Bang! cards together as one attack requiring two Missed!."""

    card_name = "Sniper"
    card_set = "fistful_of_cards"
    description = (
        "During their turn, each player may discard 2 Bang! cards together against a "
        "player. It counts as 1 Bang!, but can only be countered by 2 Missed!"
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Sniper event."""
        if game:
            game.event_flags["sniper"] = True
