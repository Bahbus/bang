from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class FistfulOfCardsEventCard(BaseEventCard):
    """Bang! a player for each card in their hand at the start of their turn."""

    card_name = "A Fistful of Cards"
    card_set = "fistful_of_cards"
    description = "Bang! equals cards in hand at turn start"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["fistful_of_cards"] = True
