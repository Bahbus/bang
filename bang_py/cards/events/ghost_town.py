from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class GhostTownEventCard(BaseEventCard):
    """Revive eliminated players with 1 health until the next event card."""

    card_name = "Ghost Town"
    description = "Eliminated players return"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        game.event_flags["ghost_town"] = True
        revived = []
        for p in game.players:
            if not p.is_alive():
                p.health = 1
                p.metadata.ghost_revived = True
                revived.append(p)
        if revived:
            game.turn_order = [i for i, pl in enumerate(game.players) if pl.is_alive()]
