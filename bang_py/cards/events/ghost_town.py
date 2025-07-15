from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class GhostTownEventCard(BaseEventCard):
    """Eliminated players temporarily return as ghosts."""

    card_name = "Ghost Town"
    card_set = "high_noon"
    description = "Eliminated players return for one turn"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["ghost_town"] = True
            game.turn_order = list(range(len(game.players)))
