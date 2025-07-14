from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class HangoverEventCard(BaseEventCard):
    """Beer cards give no health."""

    card_name = "Hangover"
    description = "Beer gives no health"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["no_beer"] = True
