"""High Noon card from the High Noon expansion. Event: everyone draws one card."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class HighNoonCard(BaseCard):
    """All players draw a card."""

    card_name = "High Noon"
    card_type = "event"
    card_set = "high_noon"
    description = "Event: everyone draws one card."

    @override
    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if not game:
            return
        for p in game.players:
            game.draw_card(p)
