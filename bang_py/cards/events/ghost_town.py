"""Ghost Town card from High Noon. Eliminated players return as ghosts for one turn."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class GhostTownEventCard(BaseEventCard):
    """Eliminated players return as ghosts for one turn with three cards."""

    card_name = "Ghost Town"
    card_set = "high_noon"
    description = (
        "During their turn, eliminated players come back as ghosts with 3 cards and "
        "cannot die. At the end of their turn, they are eliminated again."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Ghost Town event."""
        if game:
            game.event_flags["ghost_town"] = True
            game.turn_order = list(range(len(game.players)))
