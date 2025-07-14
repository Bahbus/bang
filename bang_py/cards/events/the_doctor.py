from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheDoctorEventCard(BaseEventCard):
    """Players heal 1 life instead of drawing cards."""

    card_name = "The Doctor"
    description = "Draw to heal"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["doctor"] = True
