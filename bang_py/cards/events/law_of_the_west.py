from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class LawOfTheWestEventCard(BaseEventCard):
    """All players have unlimited range."""

    card_name = "Law of the West"
    description = "Unlimited range"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["range_unlimited"] = True
