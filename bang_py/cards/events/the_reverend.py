"""The Reverend card from the High Noon expansion. Beer cannot be played and
hand limit is 2."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class TheReverendEventCard(BaseEventCard):
    """Beer cards cannot be played and hands are limited to two cards."""

    card_name = "The Reverend"
    card_set = "high_noon"
    description = "Beer cannot be played and hand limit is 2"

    @override
    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Reverend event."""
        if game:
            game.event_flags["no_beer_play"] = True
            game.event_flags["reverend_limit"] = 2
