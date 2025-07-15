from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class SniperEventCard(BaseEventCard):
    """Discard two Bang! as a single attack requiring two Missed!"""

    card_name = "Sniper"
    card_set = "fistful_of_cards"
    description = "Two Bang! counts as one"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["sniper"] = True
