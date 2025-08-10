"""Blood Brothers card from Fistful of Cards. Lose 1 life to give 1 life to another player."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class BloodBrothersEventCard(BaseEventCard):
    """Players may lose a life to heal another at the start of their turn."""

    card_name = "Blood Brothers"
    card_set = "fistful_of_cards"
    description = (
        "At the beginning of his turn, each player may choose to lose 1 life "
        "(but not their last life) to give 1 life point to any player."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Blood Brothers event."""
        if game:
            game.event_flags["blood_brothers"] = True
