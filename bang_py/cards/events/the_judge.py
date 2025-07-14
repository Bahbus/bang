from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheJudgeEventCard(BaseEventCard):
    """Beer cards cannot be played."""

    card_name = "The Judge"
    description = "Beer cards cannot be played"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["no_beer_play"] = True
