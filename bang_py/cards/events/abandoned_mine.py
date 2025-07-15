from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class AbandonedMineEventCard(BaseEventCard):
    """Draw from discard pile and discard to deck top."""

    card_name = "Abandoned Mine"
    card_set = "fistful_of_cards"
    description = "Draw from discard pile"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["abandoned_mine"] = True
