from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class RicochetEventCard(BaseEventCard):
    """Bang! cards also hit the next player."""

    card_name = "Ricochet"
    description = "Bang! hits an extra player"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["ricochet"] = True
