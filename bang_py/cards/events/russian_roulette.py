from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class RussianRouletteEventCard(BaseEventCard):
    """All players take 1 damage."""

    card_name = "Russian Roulette"
    description = "All take damage"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in list(game.players):
            p.take_damage(1)
            game.on_player_damaged(p)
