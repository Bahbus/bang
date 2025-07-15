from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class GoldRushEventCard(BaseEventCard):
    """The game proceeds counter-clockwise, but card effects still proceed clockwise."""

    card_name = "Gold Rush"
    card_set = "high_noon"
    description = "The game proceeds counter-clockwise, but card effects still proceed clockwise."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["reverse_turn"] = True
