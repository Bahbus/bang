from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class VendettaEventCard(BaseEventCard):
    """Players may draw! for another turn if they reveal a heart."""

    card_name = "Vendetta"
    card_set = "fistful_of_cards"
    description = "Draw! heart to play again"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["vendetta"] = True
