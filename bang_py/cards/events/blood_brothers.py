from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class BloodBrothersEventCard(BaseEventCard):
    """Allow players to transfer 1 life at the start of their turn."""

    card_name = "Blood Brothers"
    card_set = "fistful_of_cards"
    description = "Start of turn life transfer"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["blood_brothers"] = True
