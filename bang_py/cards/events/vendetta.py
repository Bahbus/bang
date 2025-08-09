"""Vendetta card from the Fistful of Cards expansion. At the end of their turn, each player draws!
On a heart, they may play another turn. They cannot benefit again."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class VendettaEventCard(BaseEventCard):
    """Players drawing a heart at turn end may take one extra turn."""

    card_name = "Vendetta"
    card_set = "fistful_of_cards"
    description = (
        "At the end of their turn, each player draws! On a heart, they may play "
        "another turn. They cannot benefit again."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Vendetta event."""
        if game:
            game.event_flags["vendetta"] = True
