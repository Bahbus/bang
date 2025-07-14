from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class RiverEventCard(BaseEventCard):
    """Discarded cards pass to the left player."""

    card_name = "The River"
    description = "Discarded cards pass left"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["river"] = True
