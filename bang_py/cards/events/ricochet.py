"""Ricochet card from the Fistful of Cards expansion. Bang! to discard cards in play"""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class RicochetEventCard(BaseEventCard):
    """Discard Bang! cards to shoot at cards in play."""

    card_name = "Ricochet"
    card_set = "fistful_of_cards"
    description = "Bang! to discard cards in play"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the Ricochet event."""
        if game:
            game.event_flags["ricochet"] = True
