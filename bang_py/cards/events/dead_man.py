from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class DeadManEventCard(BaseEventCard):
    """Players skip their draw phase."""

    card_name = "Dead Man"
    description = "Skip draw phase"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["no_draw"] = True
