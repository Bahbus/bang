from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class FistfulOfCardsEventCard(BaseEventCard):
    """At the beginning of his turn, each player is the target of as many Bangs! as cards in their hand."""

    card_name = "A Fistful of Cards"
    card_set = "fistful_of_cards"
    description = "At the beginning of his turn, each player is the target of as many Bangs! as cards in their hand."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["fistful_of_cards"] = True
