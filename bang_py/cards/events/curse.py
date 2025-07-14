from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class CurseEventCard(BaseEventCard):
    """Players reveal their hands."""

    card_name = "Curse"
    description = "Hands are visible"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["revealed_hands"] = True
