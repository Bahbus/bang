"""Ranch card from the Fistful of Cards expansion. Optional discard and redraw"""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class RanchEventCard(BaseEventCard):
    """Players may discard any number of cards once to draw the same amount."""

    card_name = "Ranch"
    card_set = "fistful_of_cards"
    description = "Optional discard and redraw"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Ranch event."""
        if game:
            game.event_flags["ranch"] = True
