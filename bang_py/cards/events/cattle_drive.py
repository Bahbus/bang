from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class CattleDriveEventCard(BaseEventCard):
    """Each player discards one card if possible."""

    card_name = "Cattle Drive"
    description = "Everyone discards one"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in game.players:
            if p.hand:
                p.hand.pop()
