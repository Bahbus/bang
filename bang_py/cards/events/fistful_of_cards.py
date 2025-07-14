from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class FistfulOfCardsEventCard(BaseEventCard):
    """Damage equal to cards in hand at start of turn."""

    card_name = "A Fistful of Cards"
    description = "Damage equal to cards in hand"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["damage_by_hand"] = True
